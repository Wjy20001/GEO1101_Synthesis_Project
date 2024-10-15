const BASE_URL = 'https://hogehoge.com';

export const uploadPhotos = async (
  photos: File[]
): Promise<{ lat: number; lng: number }> => {
  const formData = new FormData();
  photos.forEach((photo) => {
    formData.append('photos', photo);
  });

  const response = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to upload photos');
  }

  return response.json();
};
