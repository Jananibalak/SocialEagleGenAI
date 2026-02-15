import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { animations } from '../utils/animations';
import theme from '../config/theme';
import { toast } from 'react-toastify';
import { Upload, Check, ArrowLeft } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const CreateMentorScreen = () => {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null);
  const [topic, setTopic] = useState('');
  const [targetDays, setTargetDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <button style={styles.backButton} onClick={() => navigate('/library')}>
        <ArrowLeft size={20} />
        <span>Back</span>
      </button>

      {step === 1 && (
        <Step1FileUpload file={file} setFile={setFile} setStep={setStep} />
      )}
      {step === 2 && (
        <Step2Configure
          file={file}
          topic={topic}
          setTopic={setTopic}
          targetDays={targetDays}
          setTargetDays={setTargetDays}
          setStep={setStep}
          setLoading={setLoading}
          setProgress={setProgress}
        />
      )}
      {step === 3 && (
        <Step3Processing progress={progress} />
      )}
    </div>
  );
};

const Step1FileUpload = ({ file, setFile, setStep }) => {
  const [isDragging, setIsDragging] = useState(false);
  const dropZoneRef = useRef(null);

  useEffect(() => {
    if (dropZoneRef.current) {
      animations.pulse(dropZoneRef.current, { scale: [1, 1.02, 1], duration: 3 });
    }
  }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.docx'))) {
      setFile(droppedFile);
      setStep(2);
    } else {
      toast.error('Please upload a PDF or DOCX file');
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setStep(2);
    }
  };

  return (
    <div style={styles.stepContainer}>
      <h1 style={styles.title}>Upload Learning Material</h1>
      <p style={styles.subtitle}>Upload a PDF or DOCX file to create your AI mentor</p>

      <div
        ref={dropZoneRef}
        style={{
          ...styles.dropZone,
          borderColor: isDragging ? theme.colors.primary : '#e5e7eb',
          backgroundColor: isDragging ? `${theme.colors.primary}10` : theme.colors.white,
        }}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <Upload size={48} color={theme.colors.neutral} />
        <div style={styles.dropText}>Drag & drop your file here</div>
        <div style={styles.orText}>or</div>
        <label style={styles.uploadButton}>
          Choose File
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </label>
        <div style={styles.formats}>Supported: PDF, DOCX</div>
      </div>
    </div>
  );
};

const Step2Configure = ({ file, topic, setTopic, targetDays, setTargetDays, setStep, setLoading, setProgress }) => {
  const navigate = useNavigate();

  const handleCreate = async () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic');
      return;
    }

    setLoading(true);
    setStep(3);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('topic', topic);
    formData.append('target_days', targetDays);

    // Simulate processing steps
    const steps = [25, 50, 75, 100];
    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, 800));
      setProgress(step);
    }

    try {
      const response = await apiService.mentors.create(formData);
      toast.success('Mentor created successfully!');
      setTimeout(() => {
        navigate(`/chat/${response.data.mentor.id}`);
      }, 1500);
    } catch (error) {
      toast.error('Failed to create mentor');
      setStep(2);
      setLoading(false);
    }
  };

  return (
    <div style={styles.stepContainer}>
      <h1 style={styles.title}>Configure Your Mentor</h1>
      <div style={styles.filePreview}>
        <span>📄 {file.name}</span>
      </div>

      <div style={styles.form}>
        <div style={styles.inputGroup}>
          <label style={styles.label}>Topic/Subject</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            style={styles.input}
            placeholder="e.g., Python Programming, Calculus, etc."
          />
        </div>

        <div style={styles.inputGroup}>
          <label style={styles.label}>Learning Target: {targetDays} days</label>
          <input
            type="range"
            min="7"
            max="90"
            value={targetDays}
            onChange={(e) => setTargetDays(e.target.value)}
            style={styles.slider}
          />
        </div>

        <button onClick={handleCreate} style={styles.createButton}>
          Create Mentor
        </button>
      </div>
    </div>
  );
};

const Step3Processing = ({ progress }) => {
  const steps = [
    { text: 'Extracting text...', threshold: 25 },
    { text: 'Analyzing content...', threshold: 50 },
    { text: 'Creating learning plan...', threshold: 75 },
    { text: 'Building knowledge graph...', threshold: 100 },
  ];

  return (
    <div style={styles.stepContainer}>
      <h1 style={styles.title}>Creating Your Mentor</h1>
      <div style={styles.processingContainer}>
        {steps.map((step, index) => (
          <div key={index} style={styles.processStep}>
            <div style={{
              ...styles.checkmark,
              backgroundColor: progress >= step.threshold ? theme.colors.success : theme.colors.background,
            }}>
              {progress >= step.threshold && <Check size={16} color={theme.colors.white} />}
            </div>
            <span style={{
              ...styles.stepText,
              color: progress >= step.threshold ? theme.colors.dark : theme.colors.neutral,
            }}>
              {step.text}
            </span>
          </div>
        ))}
      </div>
      {progress === 100 && <div style={styles.successText}>✨ Success! Redirecting...</div>}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '700px',
    margin: '0 auto',
    padding: theme.spacing.xl,
  },
  backButton: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.xs,
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.neutral,
    marginBottom: theme.spacing.xl,
  },
  stepContainer: {
    textAlign: 'center',
  },
  title: {
    fontSize: theme.typography.fontSize['3xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.dark,
    marginBottom: theme.spacing.sm,
    fontFamily: theme.typography.fontFamily.display,
  },
  subtitle: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.neutral,
    marginBottom: theme.spacing.xxl,
  },
  dropZone: {
    padding: theme.spacing.xxl,
    border: '3px dashed #e5e7eb',
    borderRadius: theme.borderRadius.xl,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: theme.spacing.md,
    transition: theme.transitions.base,
  },
  dropText: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.dark,
  },
  orText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.neutral,
  },
  uploadButton: {
    padding: `${theme.spacing.md} ${theme.spacing.xl}`,
    backgroundColor: theme.colors.primary,
    color: theme.colors.dark,
    borderRadius: theme.borderRadius.md,
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    cursor: 'pointer',
  },
  formats: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.neutral,
  },
  filePreview: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.background,
    borderRadius: theme.borderRadius.md,
    marginBottom: theme.spacing.xl,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.lg,
    textAlign: 'left',
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.xs,
  },
  label: {
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.dark,
  },
  input: {
    padding: `${theme.spacing.sm} ${theme.spacing.md}`,
    fontSize: theme.typography.fontSize.base,
    border: '2px solid #e5e7eb',
    borderRadius: theme.borderRadius.md,
    outline: 'none',
  },
  slider: {
    width: '100%',
  },
  createButton: {
    padding: `${theme.spacing.md} ${theme.spacing.lg}`,
    backgroundColor: theme.colors.primary,
    color: theme.colors.dark,
    border: 'none',
    borderRadius: theme.borderRadius.md,
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.semibold,
    cursor: 'pointer',
  },
  processingContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing.lg,
    marginTop: theme.spacing.xxl,
  },
  processStep: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing.md,
  },
  checkmark: {
    width: '32px',
    height: '32px',
    borderRadius: theme.borderRadius.full,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepText: {
    fontSize: theme.typography.fontSize.lg,
  },
  successText: {
    marginTop: theme.spacing.xl,
    fontSize: theme.typography.fontSize.xl,
    color: theme.colors.success,
  },
};

export default CreateMentorScreen;
