import os
import re
from typing import Dict, List, Optional
from pathlib import Path
import PyPDF2
from docx import Document
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import logging

# ✅ FIX: Import at module level
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("⚠️ youtube-transcript-api not installed")

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Extract text from various document types"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> Dict[str, any]:
        """Extract text from PDF"""
        try:
            text = ""
            metadata = {
                'pages': 0,
                'file_type': 'pdf'
            }
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata['pages'] = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return {
                'text': text.strip(),
                'metadata': metadata,
                'success': True
            }
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return {'text': '', 'metadata': {}, 'success': False, 'error': str(e)}
    
    @staticmethod
    def extract_from_youtube(url: str) -> Dict[str, any]:
        """Extract transcript from YouTube video with better error handling"""
        print("extract_from_youtube fn",url)
        if not YOUTUBE_AVAILABLE:
            return {
                'text': '', 
                'metadata': {}, 
                'success': False, 
                'error': 'youtube-transcript-api not installed'
            }
        
        try:
            # Extract video ID
            video_id = DocumentProcessor._extract_video_id(url)
            print("id",video_id)
            if not video_id:
                return {
                    'text': '', 
                    'metadata': {}, 
                    'success': False, 
                    'error': 'Invalid YouTube URL. Please use format: https://youtube.com/watch?v=VIDEO_ID'
                }
            
            print(f"📺 Extracting transcript for video ID: {video_id}")
            
            # ✅ FIX: Try to get video info first (this will fail fast if video unavailable)
            video_title = f"YouTube Video {video_id}"
            video_author = "Unknown"
            video_duration = 0
            
            try:
                from pytube import YouTube
                yt = YouTube(url)
                video_title = yt.title
                video_author = yt.author
                video_duration = yt.length
                print(f"✅ Video info: {video_title} by {video_author}")
            except Exception as e:
                print(f"⚠️ Could not get video metadata (video might be restricted): {e}")
                # Continue anyway, we'll try transcript
            
            # ✅ FIX: Try multiple transcript methods
            transcript_list = None
            transcript_method = None
            
            # Method 1: Try English transcript
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                transcript_method = "English transcript"
                print(f"✅ Got English transcript with {len(transcript_list)} segments")
            except Exception as e1:
                print(f"⚠️ English transcript failed: {str(e1)[:100]}")
                
                # Method 2: Try any available transcript
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    transcript_method = "Auto-detected language transcript"
                    print(f"✅ Got auto transcript with {len(transcript_list)} segments")
                except Exception as e2:
                    print(f"⚠️ Auto transcript failed: {str(e2)[:100]}")
                    
                    # Method 3: Try listing and getting first available
                    try:
                        transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
                        
                        # Try to get manually created transcripts first
                        try:
                            transcript = transcript_list_obj.find_manually_created_transcript(['en'])
                            transcript_list = transcript.fetch()
                            transcript_method = "Manually created transcript"
                            print(f"✅ Got manual transcript with {len(transcript_list)} segments")
                        except:
                            # Try any available transcript
                            transcript = next(iter(transcript_list_obj))
                            transcript_list = transcript.fetch()
                            transcript_method = "Available transcript"
                            print(f"✅ Got available transcript with {len(transcript_list)} segments")
                            
                    except Exception as e3:
                        print(f"❌ All transcript methods failed: {str(e3)[:100]}")
                        
                        return {
                            'text': '', 
                            'metadata': {}, 
                            'success': False, 
                            'error': f'No transcripts available for this video. This could mean: (1) The video has no captions/subtitles, (2) The video is age-restricted or private, (3) Captions are disabled by the creator. Please try a different video or upload a document instead.'
                        }
            
            # ✅ Successfully got transcript
            if not transcript_list:
                return {
                    'text': '', 
                    'metadata': {}, 
                    'success': False, 
                    'error': 'Could not retrieve transcript from video'
                }
            
            # Combine transcript segments
            text = " ".join([item['text'] for item in transcript_list])
            
            if len(text) < 50:
                return {
                    'text': '', 
                    'metadata': {}, 
                    'success': False, 
                    'error': 'Transcript too short or empty. Video might not have proper captions.'
                }
            
            metadata = {
                'title': video_title,
                'duration': video_duration,
                'author': video_author,
                'file_type': 'youtube',
                'video_id': video_id,
                'transcript_method': transcript_method
            }
            
            print(f"✅ Extracted {len(text)} characters from YouTube using {transcript_method}")
            
            return {
                'text': text.strip(),
                'metadata': metadata,
                'success': True
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ YouTube extraction error: {error_msg}")
            
            import traceback
            traceback.print_exc()
            
            # ✅ Provide helpful error messages
            if 'no element found' in error_msg.lower() or 'xml' in error_msg.lower():
                user_error = 'Unable to access video. It might be age-restricted, private, or have disabled captions.'
            elif 'transcript' in error_msg.lower():
                user_error = 'This video has no available transcripts or captions.'
            elif 'unavailable' in error_msg.lower():
                user_error = 'Video is unavailable or has been removed.'
            else:
                user_error = f'Failed to extract YouTube transcript: {error_msg[:100]}'
            
            return {
                'text': '', 
                'metadata': {}, 
                'success': False, 
                'error': user_error
            }
    @staticmethod
    def extract_from_txt(file_path: str) -> Dict[str, any]:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            metadata = {
                'lines': len(text.split('\n')),
                'file_type': 'txt'
            }
            
            return {
                'text': text.strip(),
                'metadata': metadata,
                'success': True
            }
        except Exception as e:
            logger.error(f"TXT extraction error: {e}")
            return {'text': '', 'metadata': {}, 'success': False, 'error': str(e)}
    
    @staticmethod
    def extract_from_youtube(url: str) -> Dict[str, any]:
        """Extract transcript from YouTube video"""
        try:
            # Extract video ID
            video_id = DocumentProcessor._extract_video_id(url)
            if not video_id:
                return {'text': '', 'metadata': {}, 'success': False, 'error': 'Invalid YouTube URL'}
            
            # Get video info
            yt = YouTube(url)
            
            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join([item['text'] for item in transcript_list])
            
            metadata = {
                'title': yt.title,
                'duration': yt.length,
                'author': yt.author,
                'file_type': 'youtube'
            }
            
            return {
                'text': text.strip(),
                'metadata': metadata,
                'success': True
            }
        except Exception as e:
            logger.error(f"YouTube extraction error: {e}")
            return {'text': '', 'metadata': {}, 'success': False, 'error': str(e)}
    
    @staticmethod
    def _extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]*)',
            r'youtube\.com\/embed\/([^&\n?]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def process_document(file_path: str = None, url: str = None) -> Dict[str, any]:
        """
        Main entry point - detects type and processes document
        
        Args:
            file_path: Path to local file
            url: YouTube URL
            
        Returns:
            Dict with extracted text and metadata
        """
        if url:
            print("process_doc method")
            # YouTube video
            return DocumentProcessor.extract_from_youtube(url)
        elif file_path:
            # Local file
            ext = Path(file_path).suffix.lower()
            
            if ext == '.pdf':
                return DocumentProcessor.extract_from_pdf(file_path)
            elif ext == '.docx':
                return DocumentProcessor.extract_from_docx(file_path)
            elif ext == '.txt':
                return DocumentProcessor.extract_from_txt(file_path)
            else:
                return {'text': '', 'metadata': {}, 'success': False, 'error': f'Unsupported file type: {ext}'}
        else:
            return {'text': '', 'metadata': {}, 'success': False, 'error': 'No file or URL provided'}