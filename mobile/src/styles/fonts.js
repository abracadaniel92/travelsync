// Font configuration for React Native app
// Using Inter font family to match web app

export const fonts = {
  regular: 'System', // iOS uses SF Pro, Android uses Roboto - both are similar to Inter
  medium: 'System',
  semibold: 'System',
  bold: 'System',
};

// For iOS, we can use SF Pro which is similar to Inter
// For Android, Roboto is the default and similar
// If you want to use Inter specifically, you'd need to add it as a custom font
// For now, using system fonts which are very similar

export const fontWeights = {
  regular: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
};
