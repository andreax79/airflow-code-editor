import { toRaw } from 'vue';
import { isBookmarked, addBookmark, removeBookmark } from './bookmarks.js';

export class TabState {
    uuid; // tab id
    name;  // title
    component;  // VUE component
    target;  // target object
    initialTarget;  // initial target object (on open)
    closed;  // closed flag

    constructor(name, component, target, uuid) {
        this.name = name;
        this.component = component;
        this.target = target;
        this.initialTarget = structuredClone(target);
        this.uuid = uuid;
        this.closed = false;
    }

    addBookmark() {
        // Bookmark the tab
        return addBookmark(toRaw(this.initialTarget));
    }

    removeBookmark() {
        // Remove the bookmark
        return removeBookmark(toRaw(this.initialTarget));
    }

    isBookmarked() {
        // Check if the tab is bookmarked
        return isBookmarked(toRaw(this.initialTarget));
    }

}
