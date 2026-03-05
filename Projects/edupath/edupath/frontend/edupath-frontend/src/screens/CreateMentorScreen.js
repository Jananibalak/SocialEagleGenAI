import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { useNavigation } from '@react-navigation/native';
import { apiService } from '../services/api';
import theme from '../config/theme';
import { TextEtchingAnimation } from '../components/PageTurnTransition';

const CreateMentorScreen = () => {
  const navigation = useNavigation();
  
  const [step, setStep] = useState(1); // 1: Upload, 2: Configure, 3: Creating
  const [uploadType, setUploadType] = useState(null); // 'file' or 'youtube'
  const [selectedFile, setSelectedFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [topic, setTopic] = useState('');
  const [targetDays, setTargetDays] = useState('30');
  const [loading, setLoading] = useState(false);
  const [createdMentor, setCreatedMentor] = useState(null);

const handleFilePick = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'],
        copyToCacheDirectory: true,
      });

      console.log('📁 Document picker result:', result);

      if (result.type === 'success' || result.assets) {
        // ✅ FIX: Handle both old and new DocumentPicker API
        const fileData = result.assets ? result.assets[0] : result;
        
        console.log('✅ File selected:', fileData.name);
        setSelectedFile(fileData);
        setUploadType('file');
        setStep(2);
      } else {
        console.log('❌ File selection cancelled');
      }
    } catch (error) {
      console.error('❌ File picker error:', error);
      Alert.alert('Error', 'Failed to pick document');
    }
  };

  const handleYoutubeSubmit = () => {
    if (!youtubeUrl.includes('youtube.com') && !youtubeUrl.includes('youtu.be')) {
      Alert.alert('Invalid URL', 'Please enter a valid YouTube URL');
      return;
    }
    setUploadType('youtube');
    setStep(2);
  };

const handleCreateMentor = async () => {
    setLoading(true);
    setStep(3);

    try {
      const formData = new FormData();
      
      if (uploadType === 'file') {
        // ✅ FIX: Proper file upload for web and mobile
        const file = selectedFile;
        
        // For web
        if (file.file) {
          formData.append('file', file.file);
        } 
        // For mobile (React Native)
        else {
          formData.append('file', {
            uri: file.uri,
            type: file.mimeType || 'application/pdf',
            name: file.name,
          });
        }
        
        console.log('📄 Uploading file:', file.name);
      } else if (uploadType === 'youtube') {
        formData.append('youtube_url', youtubeUrl);
        console.log('📺 Processing YouTube:', youtubeUrl);
      }
      
      if (topic) formData.append('topic', topic);
      formData.append('target_days', targetDays);

      console.log('🚀 Creating mentor...');
      const response = await apiService.createMentor(formData);
      
      console.log('✅ Mentor created:', response.mentor);
      setCreatedMentor(response.mentor);
      
      
      // Wait 2 seconds to show mentor details, then navigate
      setTimeout(() => {
        // ✅ FIX: Navigate to Library tab specifically
        navigation.reset({
          index: 0,
          routes: [
            { 
              name: 'MainTabs',
              params: {
                screen: 'LibraryTab'
              }
            }
          ],
        });
      }, 2500);
      
    } catch (error) {
      console.error('❌ Error creating mentor:', error);
      console.error('Response data:', error.response?.data);
      
      setLoading(false);
      setStep(2);
      
      // ✅ Extract error details
      const errorData = error.response?.data || {};
      const errorMessage = errorData.error || 'Failed to create mentor. Please try again.';
      const suggestions = errorData.suggestions || [];
      const errorType = errorData.error_type;
      
      // ✅ Build alert message
      let alertMessage = errorMessage;
      
      if (suggestions.length > 0) {
        alertMessage += '\n\nSuggestions:\n';
        alertMessage += suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n');
      }
      
      // ✅ Show appropriate buttons based on error type
      const buttons = [];
      
      if (errorType === 'youtube_transcript') {
        buttons.push({
          text: 'Try Different Video',
          onPress: () => {
            setYoutubeUrl('');
            setStep(1);
          }
        });
        buttons.push({
          text: 'Upload File Instead',
          onPress: () => {
            setUploadType(null);
            setYoutubeUrl('');
            setStep(1);
          },
          style: 'default'
        });
      } else {
        buttons.push({
          text: 'Try Again',
          style: 'cancel'
        });
        buttons.push({
          text: 'Choose Different File',
          onPress: () => {
            setSelectedFile(null);
            setStep(1);
          }
        });
      }
      
      Alert.alert(
        '❌ Error Creating Mentor',
        alertMessage,
        buttons
      );
    }
  };
const renderStep1 = () => (
    <View style={styles.stepContainer}>
      <TextEtchingAnimation delay={200}>
        <Text style={styles.title}>📜 Summon a New Mentor</Text>
      </TextEtchingAnimation>
      
      <TextEtchingAnimation delay={400}>
        <Text style={styles.subtitle}>
          Share your scrolls of knowledge, and a wise mentor shall emerge
        </Text>
      </TextEtchingAnimation>

      <View style={styles.optionsContainer}>
        {/* File Upload Option */}
        <TextEtchingAnimation delay={600}>
          <TouchableOpacity
            style={styles.uploadOption}
            onPress={handleFilePick}
          >
            <Text style={styles.optionEmoji}>📄</Text>
            <Text style={styles.optionTitle}>Ancient Scrolls</Text>
            <Text style={styles.optionSubtitle}>Upload PDF, DOCX, or TXT</Text>
            
            <View style={styles.uploadHint}>
              <Text style={styles.uploadHintText}>
                📚 Supported formats: PDF, Word Documents, Text Files
              </Text>
            </View>
          </TouchableOpacity>
        </TextEtchingAnimation>

        {/* YouTube option temporarily hidden */}
      </View>
    </View>
  );

  const renderStep2 = () => (
    <View style={styles.stepContainer}>
      <TextEtchingAnimation>
        <Text style={styles.title}>⚙️ Configure Your Study</Text>
      </TextEtchingAnimation>

      <View style={styles.formContainer}>
        <Text style={styles.label}>📚 Topic (Optional)</Text>
        <Text style={styles.helperText}>
          Leave blank to let AI detect from content
        </Text>
        <TextInput
          style={styles.input}
          placeholder="e.g., Python Programming, Data Science..."
          placeholderTextColor={theme.colors.textLight}
          value={topic}
          onChangeText={setTopic}
        />

        <Text style={styles.label}>⏳ Learning Goal (Days)</Text>
        <TextInput
          style={styles.input}
          placeholder="30"
          placeholderTextColor={theme.colors.textLight}
          value={targetDays}
          onChangeText={setTargetDays}
          keyboardType="number-pad"
        />

        <View style={styles.selectedFileContainer}>
          <Text style={styles.selectedFileLabel}>Selected:</Text>
          <Text style={styles.selectedFileName}>
            {uploadType === 'file' ? selectedFile.name : youtubeUrl}
          </Text>
        </View>

        <TouchableOpacity
          style={styles.createButton}
          onPress={handleCreateMentor}
        >
          <Text style={styles.createButtonText}>✨ Summon Mentor</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.backButton}
          onPress={() => setStep(1)}
        >
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderStep3 = () => (
    <View style={styles.stepContainer}>
      {loading && !createdMentor && (
        <>
          <ActivityIndicator size="large" color={theme.colors.goldLeaf} />
          <Text style={styles.loadingText}>
            🔮 Summoning your mentor...
          </Text>
          <Text style={styles.loadingSubtext}>
            Reading ancient texts and seeking wisdom...
          </Text>
        </>
      )}

      {createdMentor && (
        <TextEtchingAnimation>
          <View style={styles.mentorReveal}>
            <Text style={styles.mentorEmoji}>{createdMentor.emoji}</Text>
            <Text style={styles.mentorName}>{createdMentor.name}</Text>
            <Text style={styles.mentorQuote}>"{createdMentor.famous_quote}"</Text>
            
            <View style={styles.mentorDetails}>
              <Text style={styles.mentorDetailLabel}>Expertise:</Text>
              <Text style={styles.mentorDetailValue}>{createdMentor.topic}</Text>
              
              <Text style={styles.mentorDetailLabel}>Teaching Style:</Text>
              <Text style={styles.mentorDetailValue}>{createdMentor.teaching_style}</Text>
              
              <Text style={styles.mentorDetailLabel}>Your Goal:</Text>
              <Text style={styles.mentorDetailValue}>
                Master in {createdMentor.target_days} days
              </Text>
            </View>

            <Text style={styles.redirectText}>
              Entering your library...
            </Text>
          </View>
        </TextEtchingAnimation>
      )}
    </View>
  );

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Decorative header */}
      <View style={styles.header}>
        <Text style={styles.ornament}>✦</Text>
        <Text style={styles.headerText}>Mentor Summoning Chamber</Text>
        <Text style={styles.ornament}>✦</Text>
      </View>

      {step === 1 && renderStep1()}
      {step === 2 && renderStep2()}
      {step === 3 && renderStep3()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    padding: theme.spacing.lg,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: theme.spacing.xl,
    paddingVertical: theme.spacing.md,
    borderBottomWidth: 2,
    borderBottomColor: theme.colors.goldLeaf,
  },
  ornament: {
    fontSize: 24,
    color: theme.colors.goldLeaf,
    marginHorizontal: theme.spacing.md,
  },
  headerText: {
    fontSize: theme.fonts.sizes.xl,
    fontWeight: 'bold',
    color: theme.colors.ink,
  },
  stepContainer: {
    alignItems: 'center',
  },
  title: {
    fontSize: theme.fonts.sizes.xxl,
    fontWeight: 'bold',
    color: theme.colors.ink,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
  },
  subtitle: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.inkFaded,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
    lineHeight: 24,
  },
  optionsContainer: {
    width: '100%',
  },
  uploadOption: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.lg,
    borderWidth: 2,
    borderColor: theme.colors.border,
    padding: theme.spacing.xl,
    marginBottom: theme.spacing.lg,
    alignItems: 'center',
    ...theme.shadows.page,
  },
  optionEmoji: {
    fontSize: 48,
    marginBottom: theme.spacing.md,
  },
  optionTitle: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: 'bold',
    color: theme.colors.ink,
    marginBottom: theme.spacing.xs,
  },
  optionSubtitle: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.inkFaded,
  },
  youtubeInput: {
    width: '100%',
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    padding: theme.spacing.md,
    marginTop: theme.spacing.md,
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.ink,
  },
  submitButton: {
    backgroundColor: theme.colors.goldLeaf,
    borderRadius: theme.borderRadius.md,
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.lg,
    marginTop: theme.spacing.md,
  },
  submitButtonDisabled: {
    backgroundColor: theme.colors.border,
  },
  submitButtonText: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: 'bold',
    color: theme.colors.ink,
  },
  formContainer: {
    width: '100%',
  },
  label: {
    fontSize: theme.fonts.sizes.md,
    fontWeight: 'bold',
    color: theme.colors.ink,
    marginBottom: theme.spacing.xs,
    marginTop: theme.spacing.md,
  },
  helperText: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.inkFaded,
    marginBottom: theme.spacing.sm,
  },
  input: {
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.md,
    borderWidth: 2,
    borderColor: theme.colors.border,
    padding: theme.spacing.md,
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.ink,
  },
  selectedFileContainer: {
    marginTop: theme.spacing.lg,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.candlelight,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.goldLeaf,
  },
  selectedFileLabel: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.inkFaded,
    marginBottom: theme.spacing.xs,
  },
  selectedFileName: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.ink,
    fontWeight: '600',
  },
  createButton: {
    backgroundColor: theme.colors.goldLeaf,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginTop: theme.spacing.xl,
    alignItems: 'center',
    ...theme.shadows.glow,
  },
  createButtonText: {
    fontSize: theme.fonts.sizes.lg,
    fontWeight: 'bold',
    color: theme.colors.ink,
  },
  backButton: {
    marginTop: theme.spacing.md,
    alignItems: 'center',
    padding: theme.spacing.md,
  },
  backButtonText: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.inkFaded,
  },
  loadingText: {
    fontSize: theme.fonts.sizes.lg,
    color: theme.colors.ink,
    marginTop: theme.spacing.lg,
    textAlign: 'center',
  },
  loadingSubtext: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.inkFaded,
    marginTop: theme.spacing.sm,
    textAlign: 'center',
  },
  mentorReveal: {
    alignItems: 'center',
    padding: theme.spacing.xl,
  },
  mentorEmoji: {
    fontSize: 80,
    marginBottom: theme.spacing.md,
  },
  mentorName: {
    fontSize: theme.fonts.sizes.xxl,
    fontWeight: 'bold',
    color: theme.colors.ink,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
  },
  mentorQuote: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.inkFaded,
    fontStyle: 'italic',
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
    paddingHorizontal: theme.spacing.lg,
  },
  mentorDetails: {
    width: '100%',
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
  },
  mentorDetailLabel: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.inkFaded,
    marginTop: theme.spacing.sm,
  },
  mentorDetailValue: {
    fontSize: theme.fonts.sizes.md,
    color: theme.colors.ink,
    fontWeight: '600',
    marginBottom: theme.spacing.sm,
  },
  redirectText: {
    fontSize: theme.fonts.sizes.sm,
    color: theme.colors.inkFaded,
    fontStyle: 'italic',
  },
});

export default CreateMentorScreen;