import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as DocumentPicker from 'expo-document-picker';
import * as ImagePicker from 'expo-image-picker';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import CollapsibleSection from '../components/CollapsibleSection';
import { Ionicons } from '@expo/vector-icons';

export default function MainScreen({ navigation }) {
  const { logout } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [travelInfo, setTravelInfo] = useState(null);
  const [calendarStatus, setCalendarStatus] = useState(null);
  const [testStatuses, setTestStatuses] = useState({});

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['image/*', 'application/pdf'],
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setSelectedFile(result.assets[0]);
        setUploadStatus(null);
        setTravelInfo(null);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick document');
    }
  };

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: false,
        quality: 1,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0];
        setSelectedFile({
          uri: asset.uri,
          name: asset.fileName || 'image.jpg',
          type: 'image/jpeg',
        });
        setUploadStatus(null);
        setTravelInfo(null);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadStatus({ type: 'processing', message: 'Processing document with AI...' });
    setTravelInfo(null);

    try {
      const result = await apiService.uploadDocument(
        selectedFile.uri,
        selectedFile.name,
        selectedFile.type || 'image/jpeg'
      );

      if (result.success) {
        setUploadStatus({ type: 'success', message: 'Document processed successfully!' });
        setTravelInfo(result.travel_info);
        if (result.calendar_event_id) {
          setCalendarStatus({ type: 'success', message: 'Event added to calendar successfully!' });
        } else {
          setCalendarStatus({ type: 'error', message: 'Could not add event to calendar.' });
        }
        setSelectedFile(null);
      } else {
        setUploadStatus({ type: 'error', message: result.message || 'Could not extract travel information.' });
      }
    } catch (error) {
      setUploadStatus({ type: 'error', message: error.message || 'An error occurred while processing the document.' });
    } finally {
      setUploading(false);
    }
  };

  const handleTest = async (testType) => {
    setTestStatuses({ ...testStatuses, [testType]: { type: 'processing', message: 'Testing...' } });

    try {
      let result;
      switch (testType) {
        case 'calendar':
          result = await apiService.testCalendar();
          break;
        case 'gemini':
          result = await apiService.testGemini();
          break;
        case 'email':
          result = await apiService.testEmail();
          break;
        default:
          return;
      }

      setTestStatuses({
        ...testStatuses,
        [testType]: {
          type: result.success ? 'success' : 'error',
          message: result.success ? 'Connection successful!' : (result.error || 'Test failed'),
        },
      });
    } catch (error) {
      setTestStatuses({
        ...testStatuses,
        [testType]: {
          type: 'error',
          message: error.message || 'Test failed',
        },
      });
    }
  };

  const handleCheckEmails = async () => {
    setTestStatuses({ ...testStatuses, email: { type: 'processing', message: 'Checking emails...' } });

    try {
      const result = await apiService.checkEmails();
      setTestStatuses({
        ...testStatuses,
        email: {
          type: result.success ? 'success' : 'error',
          message: result.message || (result.success ? 'Emails checked successfully!' : 'Failed to check emails'),
        },
      });
    } catch (error) {
      setTestStatuses({
        ...testStatuses,
        email: {
          type: 'error',
          message: error.message || 'Failed to check emails',
        },
      });
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Image
          source={require('../../assets/logo2.png')}
          style={styles.logo}
          resizeMode="contain"
        />
        <TouchableOpacity onPress={logout} style={styles.logoutButton}>
          <Text style={styles.logoutText}>Sign out</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Process Your Travel Documents</Text>
        <Text style={styles.description}>
          Upload a ticket, boarding pass, or hotel reservation to extract travel information and add it to your calendar.
        </Text>

        {/* Document Upload Section */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Document Upload</Text>

          {!selectedFile ? (
            <View style={styles.uploadArea}>
              <TouchableOpacity
                style={styles.uploadButton}
                onPress={pickImage}
                activeOpacity={0.7}
              >
                <Ionicons name="image-outline" size={48} color="#6366F1" />
                <Text style={styles.uploadText}>Select Image</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.uploadButton}
                onPress={pickDocument}
                activeOpacity={0.7}
              >
                <Ionicons name="document-outline" size={48} color="#6366F1" />
                <Text style={styles.uploadText}>Select PDF</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.fileInfo}>
              <View style={styles.fileInfoContent}>
                <Ionicons name="document" size={20} color="#6366F1" />
                <Text style={styles.fileName} numberOfLines={1}>
                  {selectedFile.name}
                </Text>
              </View>
              <TouchableOpacity
                onPress={() => {
                  setSelectedFile(null);
                  setUploadStatus(null);
                }}
                style={styles.removeButton}
              >
                <Text style={styles.removeText}>Remove</Text>
              </TouchableOpacity>
            </View>
          )}

          {selectedFile && (
            <TouchableOpacity
              style={[styles.processButton, uploading && styles.processButtonDisabled]}
              onPress={handleUpload}
              disabled={uploading}
            >
              {uploading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.processButtonText}>Process Document</Text>
              )}
            </TouchableOpacity>
          )}

          {uploadStatus && (
            <View style={[styles.statusMessage, styles[uploadStatus.type]]}>
              <Text style={[styles.statusText, styles[uploadStatus.type]]}>{uploadStatus.message}</Text>
            </View>
          )}

          {travelInfo && (
            <View style={styles.resultsSection}>
              <Text style={styles.resultsTitle}>Extracted Information</Text>
              {Object.entries(travelInfo).map(([key, value]) => (
                <View key={key} style={styles.infoItem}>
                  <Text style={styles.infoLabel}>{key.replace('_', ' ').toUpperCase()}</Text>
                  <Text style={styles.infoValue}>{value}</Text>
                </View>
              ))}
              {calendarStatus && (
                <View style={[styles.statusMessage, styles[calendarStatus.type]]}>
                  <Text style={[styles.statusText, styles[calendarStatus.type]]}>{calendarStatus.message}</Text>
                </View>
              )}
            </View>
          )}
        </View>

        {/* Email Section */}
        <CollapsibleSection title="Email Forwarding" defaultCollapsed={true}>
          <Text style={styles.cardDescription}>
            Forward emails with travel documents to automatically process them. Configure email in your environment variables.
          </Text>
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => handleTest('email')}
            >
              <Text style={styles.secondaryButtonText}>Test Email Connection</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.primaryButton}
              onPress={handleCheckEmails}
            >
              <Text style={styles.primaryButtonText}>Check & Process Emails</Text>
            </TouchableOpacity>
          </View>
          {testStatuses.email && (
            <View style={[styles.statusMessage, styles[testStatuses.email.type]]}>
              <Text style={[styles.statusText, styles[testStatuses.email.type]]}>{testStatuses.email.message}</Text>
            </View>
          )}
        </CollapsibleSection>

        {/* Calendar Section */}
        <CollapsibleSection title="Google Calendar" defaultCollapsed={true}>
          <Text style={styles.cardDescription}>
            Test your Google Calendar connection. Make sure credentials.json is configured.
          </Text>
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => handleTest('calendar')}
          >
            <Text style={styles.secondaryButtonText}>Test Calendar Connection</Text>
          </TouchableOpacity>
          {testStatuses.calendar && (
            <View style={[styles.statusMessage, styles[testStatuses.calendar.type]]}>
              <Text style={[styles.statusText, styles[testStatuses.calendar.type]]}>{testStatuses.calendar.message}</Text>
            </View>
          )}
        </CollapsibleSection>

        {/* Gemini Section */}
        <CollapsibleSection title="Test Gemini API" defaultCollapsed={true}>
          <Text style={styles.cardDescription}>
            Verify the Gemini AI connection for document processing.
          </Text>
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => handleTest('gemini')}
          >
            <Text style={styles.secondaryButtonText}>Test Gemini Connection</Text>
          </TouchableOpacity>
          {testStatuses.gemini && (
            <View style={[styles.statusMessage, styles[testStatuses.gemini.type]]}>
              <Text style={[styles.statusText, styles[testStatuses.gemini.type]]}>{testStatuses.gemini.message}</Text>
            </View>
          )}
        </CollapsibleSection>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1A365D',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 18,
    paddingVertical: 12,
    backgroundColor: 'rgba(26, 54, 93, 0.85)',
    backdropFilter: 'blur(10px)',
  },
  logo: {
    height: 70,
    width: 120,
  },
  logoutButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    backgroundColor: 'transparent',
  },
  logoutText: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: 14,
    fontWeight: '500',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 18,
    paddingBottom: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: 'white',
    marginBottom: 8,
    letterSpacing: -0.5,
  },
  description: {
    fontSize: 15,
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: 22,
    marginBottom: 24,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 18,
    marginBottom: 18,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 16,
  },
  cardDescription: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 20,
    marginBottom: 16,
  },
  uploadArea: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  uploadButton: {
    flex: 1,
    borderWidth: 2,
    borderColor: '#CBD5E1',
    borderStyle: 'dashed',
    borderRadius: 12,
    padding: 32,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F8FAFC',
  },
  uploadText: {
    marginTop: 12,
    fontSize: 14,
    fontWeight: '500',
    color: '#1E293B',
  },
  fileInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 16,
  },
  fileInfoContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 12,
  },
  fileName: {
    marginLeft: 12,
    fontSize: 14,
    fontWeight: '500',
    color: '#1E293B',
    flex: 1,
  },
  removeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  removeText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#DC2626',
  },
  processButton: {
    backgroundColor: '#6366F1',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  processButtonDisabled: {
    opacity: 0.5,
  },
  processButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  statusMessage: {
    padding: 12,
    borderRadius: 12,
    marginTop: 12,
  },
  processing: {
    backgroundColor: '#EFF6FF',
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  success: {
    backgroundColor: '#ECFDF5',
    borderWidth: 1,
    borderColor: '#A7F3D0',
  },
  error: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  statusText: {
    fontSize: 14,
    fontWeight: '500',
    textAlign: 'center',
  },
  processing: {
    color: '#2563EB',
  },
  success: {
    color: '#059669',
  },
  error: {
    color: '#DC2626',
  },
  resultsSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
  },
  resultsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 12,
  },
  infoItem: {
    padding: 12,
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366F1',
  },
  infoLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 15,
    fontWeight: '500',
    color: '#1E293B',
    lineHeight: 20,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  secondaryButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E2E8F0',
    backgroundColor: 'white',
    alignItems: 'center',
  },
  secondaryButtonText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1E293B',
  },
  primaryButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    backgroundColor: '#6366F1',
    alignItems: 'center',
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  primaryButtonText: {
    fontSize: 15,
    fontWeight: '600',
    color: 'white',
  },
});
