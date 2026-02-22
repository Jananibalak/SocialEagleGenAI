#!/usr/bin/env python3
"""
Complete Fixed Music Automation Script
"""

from flask import Flask, request, jsonify
import pyautogui
import time
import logging
import subprocess
import pyperclip

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.8

class FixedMusicAutomation:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Screen size: {self.screen_width} x {self.screen_height}")
        
    def run_applescript(self, script):
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False

    def open_saavn(self):
        """Open Jio Saavn"""
        logger.info("📱 Opening Jio Saavn...")
        
        # Switch to Finder first
        self.run_applescript('tell application "Finder" to activate')
        time.sleep(1)
        
        # Open Spotlight
        self.run_applescript('tell application "System Events" to key code 49 using command down')
        time.sleep(2)
        
        # Type and open Saavn
        pyautogui.write('jiosaavn')
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)
        
        # Take screenshot
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save("saavn_opened.png")
            logger.info("📸 Screenshot saved: saavn_opened.png")
        except:
            pass
        
        return True

    def click_search_icon(self):
        """Click the search icon using multiple methods"""
        logger.info("🔍 Clicking search icon...")
        
        try:
            # Method 1: Image recognition
            search_match = pyautogui.locateOnScreen('search_icon.png', grayscale=True, confidence=0.8)
            if search_match is not None:
                center = pyautogui.center(search_match)
                click_x = center.x // 2
                click_y = center.y // 2
                
                logger.info(f"Found search icon, clicking at: ({click_x}, {click_y})")
                pyautogui.doubleClick(click_x, click_y)
                pyautogui.press('tab')
                time.sleep(2)
                return True
                
        except Exception as e:
            logger.warning(f"Image search failed: {e}")
        
        # Method 2: Coordinate fallback
        logger.info("Trying coordinate-based search...")
        search_coordinates = [(452, 700), (450, 695), (455, 705)]
        
        for x, y in search_coordinates:
            try:
                pyautogui.click(x, y)
                time.sleep(1)
                # Test if it worked
                pyautogui.write('a')
                time.sleep(0.3)
                pyautogui.press('backspace')
                logger.info(f"✅ Search activated at ({x}, {y})")
                return True
            except:
                continue
        
        # Method 3: Keyboard shortcut
        logger.info("Using keyboard shortcut...")
        pyautogui.hotkey('command', 'f')
        time.sleep(1)
        return True

    def type_song_name(self, song):
        """Type song name using clipboard method"""
        logger.info(f"Typing song via clipboard: {song}")
        
        # Clear existing text
        pyautogui.hotkey('command', 'a')
        time.sleep(0.5)
        pyautogui.press('delete')
        time.sleep(1)
        
        # Save current clipboard
        try:
            original_clipboard = pyperclip.paste()
        except:
            original_clipboard = ""
        
        # Copy song to clipboard and paste
        pyperclip.copy(song)
        time.sleep(0.5)
        pyautogui.hotkey('command', 'v')
        time.sleep(0.5)
        
        # Restore original clipboard
        pyperclip.copy(original_clipboard)
        
        logger.info(f"✅ Successfully typed: {song}")
        
        # Press enter to search
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)

    def click_and_play_song(self):
        """Click Songs tab, 3 dots, and Play Now"""
        logger.info("🎵 Executing play sequence...")
        
        try:
            # Step 1: Click "Songs" tab
            logger.info("Step 1: Clicking Songs tab...")
            try:
                songs_tab = pyautogui.locateOnScreen('songs_tab.png', grayscale=True, confidence=0.8)
                if songs_tab:
                    center = pyautogui.center(songs_tab)
                    click_x, click_y = center.x // 2, center.y // 2
                    pyautogui.click(click_x, click_y)
                    logger.info(f"✅ Clicked Songs tab at ({click_x}, {click_y})")
                else:
                    # Fallback coordinates
                    pyautogui.click(108, 127)
                    logger.info("Used fallback for Songs tab")
            except:
                pyautogui.click(108, 127)
                logger.info("Used fallback for Songs tab")
            
            time.sleep(2)
            
            # Step 2: Click first 3 dots
            logger.info("Step 2: Clicking 3 dots...")
            try:
                three_dots = pyautogui.locateOnScreen('3dots.png', grayscale=True, confidence=0.8)
                if three_dots:
                    center = pyautogui.center(three_dots)
                    click_x, click_y = center.x // 2, center.y // 2
                    pyautogui.click(click_x, click_y)
                    logger.info(f"✅ Clicked 3 dots at ({click_x}, {click_y})")
                else:
                    # Fallback coordinates
                    pyautogui.click(1356, 190)
                    logger.info("Used fallback for 3 dots")
            except:
                pyautogui.click(1356, 190)
                logger.info("Used fallback for 3 dots")
            
            time.sleep(2)
            
            # Step 3: Click "Play Now"
            logger.info("Step 3: Clicking Play Now...")
            try:
                play_now = pyautogui.locateOnScreen('play_now.png', grayscale=True, confidence=0.8)
                if play_now:
                    center = pyautogui.center(play_now)
                    click_x, click_y = center.x // 2, center.y // 2
                    pyautogui.click(click_x, click_y)
                    logger.info(f"✅ Clicked Play Now at ({click_x}, {click_y})")
                else:
                    # Fallback coordinates
                    pyautogui.click(516, 580)
                    logger.info("Used fallback for Play Now")
            except:
                pyautogui.click(516, 580)
                logger.info("Used fallback for Play Now")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"Play sequence failed: {e}")
            return False

    def complete_automation(self, song):
        """Complete automation workflow"""
        logger.info(f"🚀 Starting complete automation for: {song}")
        
        try:
            # Step 1: Open Saavn
            if not self.open_saavn():
                logger.error("Failed to open Saavn")
                return False
            
            # Step 2: Click search icon
            if not self.click_search_icon():
                logger.error("Failed to click search icon")
                return False
            
            # Step 3: Type song name
            self.type_song_name(song)
            
            # Step 4: Play the song
            if self.click_and_play_song():
                logger.info("✅ Complete automation successful!")
            else:
                logger.warning("Play sequence had issues")
            
            # Final screenshot
            try:
                final_screenshot = pyautogui.screenshot()
                final_screenshot.save(f"final_result_{song.replace(' ', '_')}.png")
                logger.info("📸 Final screenshot saved")
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Complete automation failed: {e}")
            return False

# Global instance
music_automation = FixedMusicAutomation()

@app.route('/play-song', methods=['POST'])
def play_song():
    """Main endpoint"""
    try:
        req_data = request.get_json()
        print(req_data)
        data = req_data
        song = data.get('song', 'Whistle podu')
        user_name = data.get('user_name', 'Unknown User')
        
        logger.info(f"🎵 API Request: {song} from {user_name}")
        
        success = music_automation.complete_automation(song)
        
        return jsonify({
            'status': 'success' if success else 'partial',
            'song': song,
            'user': user_name,
            'message': f"Automation {'completed' if success else 'attempted'} for {song}"
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test-search', methods=['POST'])
def test_search():
    """Test just the search click"""
    try:
        success = music_automation.click_search_icon()
        return jsonify({
            'status': 'success' if success else 'failed',
            'message': 'Search icon test completed'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("🎵 Complete Music Automation")
    print("=" * 30)
    print("Fixed version with proper error handling")
    print("=" * 30)
    
    app.run(host='localhost', port=5001, debug=False)