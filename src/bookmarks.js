import { BOOKMARKS_KEY } from "./commons";

export function getBookmarks() {
    // Get all bookmarks from localStorage
    const bookmarks = localStorage.getItem(BOOKMARKS_KEY);
    return bookmarks ? JSON.parse(bookmarks) : [];
}

export function isBookmarked(target) {
    // Check if a bookmark already exists
    const bookmarks = getBookmarks();
    return bookmarks.some(bookmark => JSON.stringify(bookmark) === JSON.stringify(target));
}

export function addBookmark(target) {
    // Add a bookmark if it doesn't already exist
    if (!isBookmarked(target)) {
        const bookmarks = getBookmarks();
        bookmarks.push(target);
        localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
        return true;
    } else {
        return false;
    }
}

export function removeBookmark(target) {
    // Remove a bookmark
    let bookmarks = getBookmarks();
    const updatedBookmarks = bookmarks.filter(bookmark => JSON.stringify(bookmark) !== JSON.stringify(target));

    if (bookmarks.length !== updatedBookmarks.length) {
        localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(updatedBookmarks));
        return true;
    } else {
        return false;
    }
}

export function findBookmark(section, name) {
    // Find a bookmark by its section and name/path
    const bookmarks = getBookmarks();
    if (section == 'files') {
        return bookmarks.find(x => x.id == section && x.path == '/' + name);
    } else {
        return bookmarks.find(x => x.id == section && x.name == name);
    }
}
