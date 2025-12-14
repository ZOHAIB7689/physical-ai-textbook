// frontend/src/services/contentCache.js

class ContentCache {
  constructor(maxSize = 50) {
    this.cache = new Map();
    this.maxSize = maxSize;
    this.accessOrder = []; // Track access order for LRU eviction
  }

  get(key) {
    if (this.cache.has(key)) {
      // Move to end to mark as recently used
      const index = this.accessOrder.indexOf(key);
      if (index > -1) {
        this.accessOrder.splice(index, 1);
        this.accessOrder.push(key);
      }
      return this.cache.get(key);
    }
    return null;
  }

  set(key, value) {
    if (this.cache.size >= this.maxSize) {
      // Remove least recently used item
      const lruKey = this.accessOrder.shift();
      this.cache.delete(lruKey);
    }
    
    this.cache.set(key, value);
    this.accessOrder.push(key);
  }

  has(key) {
    return this.cache.has(key);
  }

  clear() {
    this.cache.clear();
    this.accessOrder = [];
  }

  // Preload content for better performance
  async preloadContent(keys, loaderFn) {
    const promises = [];
    
    for (const key of keys) {
      if (!this.has(key)) {
        promises.push(
          loaderFn(key)
            .then(data => {
              this.set(key, data);
              return { key, data, error: null };
            })
            .catch(error => {
              return { key, data: null, error };
            })
        );
      }
    }
    
    return Promise.all(promises);
  }
}

export default new ContentCache();