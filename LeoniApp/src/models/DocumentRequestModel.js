class DocumentRequestModel {
  constructor() {
    this.document = {
      name: '',
      status: {
        current: ['en attente'],
        progress: [
          {step: ['en attente'], date: null, completed: false},
          {step: ['en cours'], date: null, completed: false}, 
          {step: ['accepté'], date: null, completed: false},
          {step: ['refusé'], date: null, completed: false},
          {step: ['livré'], date: null, completed: false}
        ]
      }
    };
  }

  getDocument() {
    // Return deep copy of document
    return JSON.parse(JSON.stringify(this.document));
  }

  updateStatus(newStatus) {
    const statusIndex = this.document.status.progress.findIndex(s => s.step.includes(newStatus[0]));
    if (statusIndex >= 0) {
      // Update all steps up to current one
      this.document.status.progress.forEach((step, index) => {
        this.document.status.progress[index].completed = index <= statusIndex;
        this.document.status.progress[index].date = new Date();
      });
      this.document.status.current = newStatus;
      this.notify();
    }
  }

  getCurrentStatus() {
    return this.document.status.current;
  }

  getStatusHistory() {
    return this.document.status.progress;
  }

  subscribe(callback) {
    this.onChange = callback;
  }

  notify() {
    if (this.onChange) {
      this.onChange(this.getDocument());
    }
  }
}

export default DocumentRequestModel;
