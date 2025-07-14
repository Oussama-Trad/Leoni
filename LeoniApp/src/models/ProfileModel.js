class ProfileModel {
  constructor() {
    this.profileData = {
      firstName: '',
      lastName: '',
      email: '',
      parentalEmail: '',
      phoneNumber: '',
      parentalPhoneNumber: ''
    };
    this.isEditing = false;
    this.isLoading = false;
  }

  // Getters
  getProfileData() {
    return { ...this.profileData };
  }

  getIsEditing() {
    return this.isEditing;
  }

  getIsLoading() {
    return this.isLoading;
  }

  // Setters
  setProfileData(data) {
    this.profileData = { ...this.profileData, ...data };
    this.notify();
  }

  setField(field, value) {
    this.profileData[field] = value;
    this.notify();
  }

  setIsEditing(value) {
    this.isEditing = value;
    this.notify();
  }

  setIsLoading(value) {
    this.isLoading = value;
    this.notify();
  }

  // Méthodes d'abonnement aux changements
  subscribe(callback) {
    this.onChange = callback;
  }

  notify() {
    if (this.onChange) {
      this.onChange({
        ...this.profileData,
        isEditing: this.isEditing,
        isLoading: this.isLoading
      });
    }
  }
}

export default ProfileModel;
