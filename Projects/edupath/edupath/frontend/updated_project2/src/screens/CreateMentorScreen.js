import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  StyleSheet,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';
import Animated, {
  FadeInDown,
  FadeInRight,
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withSequence,
  withTiming,
  withSpring,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import { apiService } from '../services/api';
import Colors from '../constants/colors';

const ICON_OPTIONS = [
  'book-open', 'cpu', 'code', 'globe', 'layers',
  'terminal', 'zap', 'award', 'compass', 'feather',
];

const MENTOR_NAMES = [
  'Atlas', 'Nova', 'Sage', 'Echo', 'Orion',
  'Luna', 'Zen', 'Aria', 'Pixel', 'Spark',
];

const ProcessingStep = ({ label, completed, index }) => {
  const checkScale = useSharedValue(0);

  useEffect(() => {
    if (completed) {
      checkScale.value = withSpring(1, { damping: 8 });
    }
  }, [completed]);

  const checkStyle = useAnimatedStyle(() => ({
    transform: [{ scale: checkScale.value }],
  }));

  return (
    <Animated.View entering={FadeInDown.delay(index * 100).duration(400)} style={styles.processStep}>
      <Animated.View style={[styles.processCheck, checkStyle]}>
        {completed ? (
          <Feather name="check-circle" size={20} color={Colors.success} />
        ) : (
          <ActivityIndicator size="small" color={Colors.accent} />
        )}
      </Animated.View>
      <Text style={[styles.processLabel, completed && styles.processLabelDone]}>{label}</Text>
    </Animated.View>
  );
};

const CreateMentorScreen = () => {
  const navigation = useNavigation();
  const insets = useSafeAreaInsets();
  const [step, setStep] = useState(1);
  const [uploadType, setUploadType] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [topic, setTopic] = useState('');
  const [mentorName, setMentorName] = useState('');
  const [targetDays, setTargetDays] = useState('30');
  const [selectedIcon, setSelectedIcon] = useState('book-open');
  const [loading, setLoading] = useState(false);
  const [processSteps, setProcessSteps] = useState([false, false, false, false]);

  const borderPulse = useSharedValue(0);

  useEffect(() => {
    borderPulse.value = withRepeat(
      withSequence(
        withTiming(1, { duration: 1500 }),
        withTiming(0, { duration: 1500 })
      ),
      -1,
      true
    );
  }, []);

  const dropZoneStyle = useAnimatedStyle(() => ({
    borderColor: `rgba(245, 203, 125, ${0.2 + borderPulse.value * 0.4})`,
  }));

  const handleFilePick = async () => {
    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'],
        copyToCacheDirectory: true,
      });

      if (result.type === 'success' || result.assets) {
        const fileData = result.assets ? result.assets[0] : result;
        setSelectedFile(fileData);
        setUploadType('file');
        const autoName = MENTOR_NAMES[Math.floor(Math.random() * MENTOR_NAMES.length)];
        setMentorName(autoName);
        setStep(2);
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }
    } catch (error) {
      console.error('File picker error:', error);
      Alert.alert('Error', 'Failed to pick document');
    }
  };

  const handleYoutubeSubmit = () => {
    if (!youtubeUrl.includes('youtube.com') && !youtubeUrl.includes('youtu.be')) {
      Alert.alert('Invalid URL', 'Please enter a valid YouTube URL');
      return;
    }
    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setUploadType('youtube');
    const autoName = MENTOR_NAMES[Math.floor(Math.random() * MENTOR_NAMES.length)];
    setMentorName(autoName);
    setStep(2);
  };

  const handleCreateMentor = async () => {
    if (!topic.trim() || !mentorName.trim()) {
      Alert.alert('Missing Information', 'Please fill in all required fields');
      return;
    }

    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    setLoading(true);
    setStep(3);

    // Simulate processing steps
    for (let i = 0; i < 4; i++) {
      await new Promise((r) => setTimeout(r, 800 + Math.random() * 400));
      setProcessSteps((prev) => {
        const next = [...prev];
        next[i] = true;
        return next;
      });
    }

    try {
      const formData = new FormData();

      if (uploadType === 'file') {
        const file = selectedFile;
        if (file.file) {
          formData.append('file', file.file);
        } else {
          formData.append('file', {
            uri: file.uri,
            type: file.mimeType || 'application/pdf',
            name: file.name,
          });
        }
      } else if (uploadType === 'youtube') {
        formData.append('youtube_url', youtubeUrl);
      }

      formData.append('topic', topic);
      formData.append('target_days', targetDays);
      formData.append('emoji', selectedIcon);

      const response = await apiService.createMentor(formData);

      if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      
      Alert.alert('Success!', 'Your mentor has been created', [
        {
          text: 'Start Learning',
          onPress: () => navigation.navigate('MentorChat', {
            mentorId: response.mentor.id,
            mentorName: mentorName,
          }),
        },
      ]);
    } catch (error) {
      console.error('Error creating mentor:', error);
      if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      Alert.alert('Error', error.response?.data?.error || 'Failed to create mentor');
      setStep(2);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <Pressable
          onPress={() => {
            if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            navigation.goBack();
          }}
          hitSlop={12}
          style={styles.headerBack}
        >
          <Feather name="x" size={22} color={Colors.white} />
        </Pressable>
        <Text style={styles.headerTitle}>Create Mentor</Text>
        <View style={{ width: 36 }} />
      </View>

      <ScrollView
        contentContainerStyle={[
          styles.scrollContent,
          { paddingBottom: insets.bottom + 40 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        {step === 1 && (
          <Animated.View entering={FadeInRight.duration(400)} key="step1">
            <Text style={styles.stepTitle}>Upload Material</Text>
            <Text style={styles.stepSubtitle}>Choose your learning source</Text>

            <Animated.View style={[styles.dropZone, dropZoneStyle]}>
              <LinearGradient
                colors={['rgba(245, 203, 125, 0.1)', 'rgba(245, 203, 125, 0.05)']}
                style={styles.dropZoneGradient}
              >
                <Feather name="upload-cloud" size={48} color={Colors.accent} />
                <Text style={styles.dropZoneTitle}>Upload Document</Text>
                <Text style={styles.dropZoneText}>PDF, DOCX, or TXT</Text>
                <Pressable style={styles.dropZoneButton} onPress={handleFilePick}>
                  <Text style={styles.dropZoneButtonText}>Choose File</Text>
                </Pressable>
              </LinearGradient>
            </Animated.View>

            <View style={styles.divider}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>OR</Text>
              <View style={styles.dividerLine} />
            </View>

            <View style={styles.youtubeSection}>
              <Feather name="youtube" size={24} color={Colors.accent} style={styles.youtubeIcon} />
              <Text style={styles.youtubeTitle}>YouTube Video</Text>
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  placeholder="Paste YouTube URL"
                  placeholderTextColor={Colors.textMuted}
                  value={youtubeUrl}
                  onChangeText={setYoutubeUrl}
                  autoCapitalize="none"
                />
              </View>
              <Pressable
                style={styles.youtubeButton}
                onPress={handleYoutubeSubmit}
                disabled={!youtubeUrl.trim()}
              >
                <LinearGradient
                  colors={youtubeUrl.trim() ? [Colors.accent, Colors.accentDark] : ['rgba(255,255,255,0.1)', 'rgba(255,255,255,0.1)']}
                  style={styles.youtubeButtonGradient}
                >
                  <Text style={[styles.youtubeButtonText, !youtubeUrl.trim() && styles.youtubeButtonTextDisabled]}>
                    Continue
                  </Text>
                </LinearGradient>
              </Pressable>
            </View>
          </Animated.View>
        )}

        {step === 2 && (
          <Animated.View entering={FadeInRight.duration(400)} key="step2">
            <Text style={styles.stepTitle}>Configure Mentor</Text>
            <Text style={styles.stepSubtitle}>Personalize your learning experience</Text>

            <View style={styles.formSection}>
              <Text style={styles.label}>Select Icon</Text>
              <View style={styles.iconGrid}>
                {ICON_OPTIONS.map((icon, index) => (
                  <Pressable
                    key={icon}
                    onPress={() => {
                      setSelectedIcon(icon);
                      if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                    }}
                    style={styles.iconOption}
                  >
                    <LinearGradient
                      colors={selectedIcon === icon
                        ? [Colors.accent, Colors.accentDark]
                        : ['rgba(255,255,255,0.06)', 'rgba(255,255,255,0.06)']
                      }
                      style={styles.iconGradient}
                    >
                      <Feather
                        name={icon}
                        size={24}
                        color={selectedIcon === icon ? Colors.primaryDark : Colors.white}
                      />
                    </LinearGradient>
                  </Pressable>
                ))}
              </View>

              <Text style={styles.label}>Mentor Name</Text>
              <View style={styles.inputContainer}>
                <Feather name="user" size={18} color={Colors.textSecondary} />
                <TextInput
                  style={styles.input}
                  placeholder="e.g., Atlas, Nova, Sage"
                  placeholderTextColor={Colors.textMuted}
                  value={mentorName}
                  onChangeText={setMentorName}
                />
              </View>

              <Text style={styles.label}>Topic / Subject</Text>
              <View style={styles.inputContainer}>
                <Feather name="bookmark" size={18} color={Colors.textSecondary} />
                <TextInput
                  style={styles.input}
                  placeholder="e.g., Machine Learning, History"
                  placeholderTextColor={Colors.textMuted}
                  value={topic}
                  onChangeText={setTopic}
                />
              </View>

              <Text style={styles.label}>Target Learning Days</Text>
              <View style={styles.inputContainer}>
                <Feather name="calendar" size={18} color={Colors.textSecondary} />
                <TextInput
                  style={styles.input}
                  placeholder="30"
                  placeholderTextColor={Colors.textMuted}
                  value={targetDays}
                  onChangeText={setTargetDays}
                  keyboardType="numeric"
                />
              </View>

              <Pressable style={styles.createButton} onPress={handleCreateMentor}>
                <LinearGradient
                  colors={[Colors.accent, Colors.accentDark]}
                  style={styles.createButtonGradient}
                >
                  <Text style={styles.createButtonText}>Create Mentor</Text>
                  <Feather name="arrow-right" size={18} color={Colors.primaryDark} />
                </LinearGradient>
              </Pressable>
            </View>
          </Animated.View>
        )}

        {step === 3 && (
          <Animated.View entering={FadeInRight.duration(400)} key="step3" style={styles.processingContainer}>
            <LinearGradient
              colors={[Colors.accent, Colors.accentDark]}
              style={styles.processingIcon}
            >
              <Feather name="zap" size={40} color={Colors.primaryDark} />
            </LinearGradient>
            <Text style={styles.processingTitle}>Creating Your Mentor</Text>
            <Text style={styles.processingText}>This will take a few moments...</Text>

            <View style={styles.processSteps}>
              <ProcessingStep label="Analyzing content" completed={processSteps[0]} index={0} />
              <ProcessingStep label="Extracting knowledge" completed={processSteps[1]} index={1} />
              <ProcessingStep label="Building learning path" completed={processSteps[2]} index={2} />
              <ProcessingStep label="Finalizing mentor" completed={processSteps[3]} index={3} />
            </View>
          </Animated.View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.06)',
  },
  headerBack: {
    width: 36,
    height: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 18,
    color: Colors.white,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 24,
  },
  stepTitle: {
    fontFamily: 'Inter_700Bold',
    fontSize: 24,
    color: Colors.white,
    marginBottom: 6,
  },
  stepSubtitle: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 24,
  },
  dropZone: {
    borderRadius: 16,
    borderWidth: 2,
    borderStyle: 'dashed',
    overflow: 'hidden',
  },
  dropZoneGradient: {
    padding: 40,
    alignItems: 'center',
  },
  dropZoneTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 18,
    color: Colors.white,
    marginTop: 16,
    marginBottom: 4,
  },
  dropZoneText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 20,
  },
  dropZoneButton: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
  },
  dropZoneButtonText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.white,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 32,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  dividerText: {
    fontFamily: 'Inter_500Medium',
    fontSize: 12,
    color: Colors.textMuted,
    marginHorizontal: 16,
  },
  youtubeSection: {
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  youtubeIcon: {
    marginBottom: 8,
  },
  youtubeTitle: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.white,
    marginBottom: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.inputBg,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.inputBorder,
    paddingHorizontal: 14,
    height: 52,
    marginBottom: 12,
  },
  input: {
    flex: 1,
    fontFamily: 'Inter_400Regular',
    fontSize: 15,
    color: Colors.white,
    marginLeft: 10,
  },
  youtubeButton: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  youtubeButtonGradient: {
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  youtubeButtonText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.primaryDark,
  },
  youtubeButtonTextDisabled: {
    color: Colors.textMuted,
  },
  formSection: {
    gap: 16,
  },
  label: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 14,
    color: Colors.white,
    marginBottom: 8,
  },
  iconGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 8,
  },
  iconOption: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  iconGradient: {
    width: 56,
    height: 56,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
  },
  createButton: {
    borderRadius: 12,
    overflow: 'hidden',
    marginTop: 8,
  },
  createButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 16,
  },
  createButtonText: {
    fontFamily: 'Inter_600SemiBold',
    fontSize: 16,
    color: Colors.primaryDark,
  },
  processingContainer: {
    alignItems: 'center',
    paddingTop: 40,
  },
  processingIcon: {
    width: 88,
    height: 88,
    borderRadius: 44,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  processingTitle: {
    fontFamily: 'Inter_700Bold',
    fontSize: 22,
    color: Colors.white,
    marginBottom: 6,
  },
  processingText: {
    fontFamily: 'Inter_400Regular',
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 40,
  },
  processSteps: {
    width: '100%',
    gap: 16,
  },
  processStep: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: 'rgba(255,255,255,0.04)',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  processCheck: {
    width: 24,
    height: 24,
  },
  processLabel: {
    fontFamily: 'Inter_500Medium',
    fontSize: 15,
    color: Colors.textSecondary,
  },
  processLabelDone: {
    color: Colors.white,
  },
});

export default CreateMentorScreen;
