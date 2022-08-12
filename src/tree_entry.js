import { prepareHref } from './commons';

export function getIcon(path, type) {
    // Get icon for a given path/type
    if (type == 'tree') {
        return 'folder';
    } else {
        const extension = (path.substring(path.lastIndexOf('.') + 1) || '').toLowerCase();
        if ([ 'zip', 'tar', 'tgz', 'tbz2', 'txz', 'z', 'gz', 'xz', 'bz', 'bz2', '7z', 'lz' ].indexOf(extension) != -1) {
            return 'folder_zip';
        } else if ([ 'jpg', 'jpeg', 'png', 'svg', 'git', 'bmp', 'ief', 'tif', 'tiff', 'ico' ].indexOf(extension) != -1) {
            return 'image';
        } else if ([ 'py' ].indexOf(extension) != -1) {
            return 'description';
        } else {
            return 'file';
        }
    }
}

export function formatSize(size, type) {
    // size - https://en.wikipedia.org/wiki/Kilobyte
    if (isNaN(size)) {
        return "";
    } else if (type == 'tree') { // tree - number of files in the folder
        if (size == null) {
            return "";
        } else if (size == 1) {
            return size + ' item';
        } else {
            return size + ' items';
        }
    } else if (size < 10**3) {
        return size.toString() + " B";
    } else if (size < 10**6) {
        return (size / 10**3).toFixed(2) + " kB";
    } else if (size < 10**9) {
        return (size / 10**6).toFixed(2) + " MB";
    } else {
        return (size / 10**9).toFixed(2) + " GB";
    }
}

export class TreeEntry {
    // File tree item
    constructor(data, isGit, path) {
        const self = this;
        if (data) {
            self.mode = data.mode;
            self.isGit = isGit;
            self.type = data.leaf ? 'blob' : 'tree';
            if (self.isGit) {
                self.object = data.id;
            } else {
                self.object = (path || '') + '/' + data.id;
            }
            self.mtime = data.mtime ? data.mtime.replace('T', ' ') : '';
            self.size = data.size;
            self.name = data.label || data.id;
            self.isSymbolicLink = (self.mode & 120000) == 120000; // S_IFLNK
            self.icon = getIcon(self.name, self.type);
            // href
            if (self.isGit) { // git blob
                self.href = prepareHref('repo/' + self.object + '/' + self.name);
            } else { // local file/dir
                if (self.type == 'tree') {
                    self.href = '#files' + encodeURI(self.object);
                } else {
                    self.href = '#edit' + encodeURI(self.object);
                }
            }
            // download href
            if (self.type == 'tree') { // tree
                self.downloadHref = '#';
            } else if (self.isGit) { // git blob
                self.downloadHref = prepareHref('repo/' + self.object + '/' + self.name);
            } else { // local file
                self.downloadHref = prepareHref('files/' + self.object);
            }
            // size
            self.formattedSize = formatSize(self.size, self.type);
        }
    }
}
