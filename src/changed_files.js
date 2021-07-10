/*
 * Copyright 2015 Eric ALBER
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { git } from "./commons";

function splitLines(data) {
    return data.split("\n").filter(function(s) { return s.length > 0; });
};

function getNodeIndex(element) {
    let index = 0;
    while (element.previousElementSibling) {
        element = element.previousElementSibling;
        ++index;
    }
    return index;
}

export function ChangedFilesView(workspaceView, type, label) {
    let self = this;

    self.update = function() {
        jQuery(fileList).empty()
        let col = type == "working-copy" ? 1 : 0;
        git([ "status", "--porcelain" ], function(data) {
            self.filesCount = 0;
            splitLines(data).forEach(function(line) {
                let status = line[col];
                if (col == 0 && status != " " && status != "?" || col == 1 && status != " ") {
                    ++self.filesCount;
                    let item = jQuery('<a class="list-group-item">').appendTo(fileList)[0];
                    item.status = status;
                    line = line.substr(3);
                    let splitted = line.split(" -> ");
                    if (splitted.length > 1) {
                        item.model = splitted[1];
                    } else {
                        item.model = line
                    }
                    item.appendChild(document.createTextNode(line));
                    jQuery(item).click(self.select);
                    jQuery(item).dblclick(self.process);
                }
            });
            if (selectedIndex !== null && selectedIndex >= fileList.childElementCount) {
                selectedIndex = fileList.childElementCount - 1;
                if (selectedIndex == -1) {
                    selectedIndex = null;
                }
            }
            if (selectedIndex !== null) {
                let selectedNode = fileList.children[selectedIndex];
                jQuery(selectedNode).addClass("active");
                self.refreshDiff(selectedNode);
            }
            fileListContainer.scrollTop = prevScrollTop;
        });
    };

    self.select = function(event) {
        let clicked = event.target;

        if (event.shiftKey && selectedIndex !== null) {
            let clickedIndex = getNodeIndex(clicked);
            let from;
            let to;
            if (clickedIndex < selectedIndex) {
                from = clickedIndex;
                to = selectedIndex;
            } else {
                from = selectedIndex;
                to = clickedIndex;
            }
            for (let i = from; i <= to; ++i) {
                jQuery(fileList.children[i]).addClass("active");
            }
            selectedIndex = clickedIndex;
        } else if (event.ctrlKey) {
            jQuery(clicked).toggleClass("active");
            selectedIndex = getNodeIndex(clicked);
        } else {
            for (let i = 0; i < fileList.childElementCount; ++i) {
                jQuery(fileList.children[i]).removeClass("active");
            }
            jQuery(clicked).addClass("active");
            selectedIndex = getNodeIndex(clicked);
        }
        if (type == "working-copy") {
            workspaceView.stagingAreaView.unselect();
        } else {
            workspaceView.workingCopyView.unselect();
        }
        self.refreshDiff(clicked);
    };

    self.refreshDiff = function(element) {
        let cmd = [ "diff" ];
        if (type == "staging-area") {
            cmd.push("--cached");
        }
        workspaceView.diffView.update(cmd, undefined, [ element.model ] , type == "working-copy" ? "stage" : "unstage");
    };

    self.unselect = function() {
        if (selectedIndex !== null) {
            jQuery(fileList.children[selectedIndex]).removeClass("active");
            selectedIndex = null;
        }
    };

    self.getFileList = function(including, excluding) {
        let files = [];
        for (let i = 0; i < fileList.childElementCount; ++i) {
            let child = fileList.children[i];
            let included = including == undefined || including.indexOf(child.status) != -1;
            let excluded = excluding != undefined && excluding.indexOf(child.status) != -1;
            if (jQuery(child).hasClass("active") && included && !excluded) {
                files.push(child.model);
            }
        }
        return files;
    }

    self.process = function() {
        prevScrollTop = fileListContainer.scrollTop;
        let files = self.getFileList(undefined, "D");
        let rmFiles = self.getFileList("D");
        if (files.length != 0) {
            let cmd = type == "working-copy" ? ["add"] : ["reset"];
            cmd.push('--');
            git(cmd.concat(files), function(data) {
                if (rmFiles.length != 0) {
                    let cmd = [ 'rm', '--'];
                    git(cmd.concat(rmFiles), function(data) {
                        workspaceView.update(type == "working-copy" ? ["stage"] : ["unstage"]);
                    });
                } else {
                    workspaceView.update(type == "working-copy" ? ["stage"] : ["unstage"]);
                }
            });
        } else if (rmFiles.length != 0) {
            let cmd = type == "working-copy" ? ["rm"] : ["reset"];
            cmd.push('--')
            git(cmd.concat(rmFiles), function(data) {
                workspaceView.update(type == "working-copy" ? ["stage"] : ["unstage"]);
            });
        }
    };

    self.checkout = function() {
        prevScrollTop = fileListContainer.scrollTop;
        let files = self.getFileList();
        if (files.length != 0) {
            let cmd = [ 'checkout' ];
            git(cmd.concat(files), function(data) {
                workspaceView.update(["stage"]);
            });
        }
    }

    self.getSelectedItemsCount = function() {
        return jQuery(".active", fileList).length;
    }

    self.element = jQuery(   '<div id="' + type + '-view" class="panel panel-default">' +
                            '<div class="panel-heading">' +
                                '<h5>'+ label + '</h5>' +
                                '<div class="btn-group btn-group-sm"></div>' +
                            '</div>' +
                            '<div class="file-list-container">' +
                                '<div class="list-group"></div>' +
                            '</div>' +
                        '</div>')[0];
    let buttons = (type == "working-copy") ?
        [{ name: "Stage", callback: self.process }, { name: "Revert", callback: self.checkout }] :
        [{ name: "Unstage", callback: self.process }];
    let btnGroup = jQuery(".btn-group", self.element);
    buttons.forEach(function (btnData) {
        let btn = jQuery('<button type="button" class="btn btn-default">' + btnData.name + '</button>')
        btn.appendTo(btnGroup);
        btn.click(btnData.callback);
    });
    let fileListContainer = jQuery(".file-list-container", self.element)[0];
    let prevScrollTop = fileListContainer.scrollTop;
    let fileList = jQuery(".list-group", fileListContainer)[0];
    let selectedIndex = null;

    self.filesCount = 0;
};
