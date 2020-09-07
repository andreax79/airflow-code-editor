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

"use strict"

var webui = webui || {};

webui.repo = "root";

webui.COLORS = ["#ffab1d", "#fd8c25", "#f36e4a", "#fc6148", "#d75ab6", "#b25ade", "#6575ff", "#7b77e9", "#4ea8ec", "#00d0f5", "#4eb94e", "#51af23", "#8b9f1c", "#d0b02f", "#d0853a", "#a4a4a4",
                "#ffc51f", "#fe982c", "#fd7854", "#ff705f", "#e467c3", "#bd65e9", "#7183ff", "#8985f7", "#55b6ff", "#10dcff", "#51cd51", "#5cba2e", "#9eb22f", "#debe3d", "#e19344", "#b8b8b8",
                "#ffd03b", "#ffae38", "#ff8a6a", "#ff7e7e", "#ef72ce", "#c56df1", "#8091ff", "#918dff", "#69caff", "#3ee1ff", "#72da72", "#71cf43", "#abbf3c", "#e6c645", "#eda04e", "#c5c5c5",
                "#ffd84c", "#ffb946", "#ff987c", "#ff8f8f", "#fb7eda", "#ce76fa", "#90a0ff", "#9c98ff", "#74cbff", "#64e7ff", "#7ce47c", "#85e357", "#b8cc49", "#edcd4c", "#f9ad58", "#d0d0d0",
                "#ffe651", "#ffbf51", "#ffa48b", "#ff9d9e", "#ff8de1", "#d583ff", "#97a9ff", "#a7a4ff", "#82d3ff", "#76eaff", "#85ed85", "#8deb5f", "#c2d653", "#f5d862", "#fcb75c", "#d7d7d7",
                "#fff456", "#ffc66d", "#ffb39e", "#ffabad", "#ff9de5", "#da90ff", "#9fb2ff", "#b2afff", "#8ddaff", "#8bedff", "#99f299", "#97f569", "#cde153", "#fbe276", "#ffc160", "#e1e1e1",
                "#fff970", "#ffd587", "#ffc2b2", "#ffb9bd", "#ffa5e7", "#de9cff", "#afbeff", "#bbb8ff", "#9fd4ff", "#9aefff", "#b3f7b3", "#a0fe72", "#dbef6c", "#fcee98", "#ffca69", "#eaeaea",
                "#763700", "#9f241e", "#982c0e", "#a81300", "#80035f", "#650d90", "#082fca", "#3531a3", "#1d4892", "#006f84", "#036b03", "#236600", "#445200", "#544509", "#702408", "#343434",
                "#9a5000", "#b33a20", "#b02f0f", "#c8210a", "#950f74", "#7b23a7", "#263dd4", "#4642b4", "#1d5cac", "#00849c", "#0e760e", "#287800", "#495600", "#6c5809", "#8d3a13", "#4e4e4e",
                "#c36806", "#c85120", "#bf3624", "#df2512", "#aa2288", "#933bbf", "#444cde", "#5753c5", "#1d71c6", "#0099bf", "#188018", "#2e8c00", "#607100", "#907609", "#ab511f", "#686868",
                "#e47b07", "#e36920", "#d34e2a", "#ec3b24", "#ba3d99", "#9d45c9", "#4f5aec", "#615dcf", "#3286cf", "#00abca", "#279227", "#3a980c", "#6c7f00", "#ab8b0a", "#b56427", "#757575",
                "#ff911a", "#fc8120", "#e7623e", "#fa5236", "#ca4da9", "#a74fd3", "#5a68ff", "#6d69db", "#489bd9", "#00bcde", "#36a436", "#47a519", "#798d0a", "#c1a120", "#bf7730", "#8e8e8e"]


webui.showError = function(message) {
    jQuery("#error-modal .alert").text(message);
    jQuery("#error-modal").modal('show');
}

webui.showWarning = function(message) {
    var messageBox = jQuery("#message-box");
    messageBox.empty();
    jQuery(  '<div class="alert alert-warning alert-dismissible" role="alert">' +
            '<button type="button" class="close" data-dismiss="alert">' +
                '<span aria-hidden="true">&times;</span>' +
                '<span class="sr-only">Close</span>' +
            '</button>' +
            message +
        '</div>').appendTo(messageBox);
}

webui.git = function(args, callback) {
    jQuery.ajax({
        type: 'POST',
        url: 'repo',
        data: { args: args },
        success: function(data, textStatus, request) {
            var messageStartIndex = data.length - parseInt(request.getResponseHeader('X-Git-Stderr-Length'));
            var rcode = parseInt(request.getResponseHeader('X-Git-Return-Code'));
            var output = data.substring(0, messageStartIndex);
            var message = data.substring(messageStartIndex);
            if (rcode === 0) {
                if (callback) {
                    callback(output);
                }
                // Return code is 0 but there is stderr output: this is a warning message
                if (message.length > 0) {
                    webui.showWarning(message);
                }
                jQuery("#error-modal .alert").text("");
            } else {
                webui.showError(message);
            }
        },
        error: function (request, textStatus, errorThrown) {
            webui.showError(errorThrown);
        }
    });
};

webui.detachChildren = function(element) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

webui.splitLines = function(data) {
    return data.split("\n").filter(function(s) { return s.length > 0; });
};

webui.getNodeIndex = function(element) {
    var index = 0;
    while (element.previousElementSibling) {
        element = element.previousElementSibling;
        ++index;
    }
    return index;
}

webui.TabBox = function(buttons) {

    var self = this;

    self.itemClicked = function(event) {
        self.updateSelection(event.target.parentElement);
    }

    self.select = function(index) {
        self.updateSelection(self.element.children[index]);
    }

    self.updateSelection = function(elt) {
        jQuery(".active", self.element).removeClass("active");
        jQuery(elt).addClass("active");
        elt.callback();
    }

    self.element = jQuery('<ul class="nav nav-pills nav-justified" role="tablist">')[0];

    for (var i = 0; i < buttons.length; ++i) {
        var item = buttons[i];
        var li = jQuery('<li><a href="#">' + item[0] + '</a></li>');
        li.appendTo(self.element);
        li.click(self.itemClicked);
        li[0].callback = item[1];
    }
};

/*
 * == SideBarView =============================================================
 */
webui.SideBarView = function(mainView) {

    var self = this;

    self.selectRef = function(refName) {
        var selected = jQuery(".active", self.element);
        if (selected.length > 0) {
            if (selected[0].refName != refName) {
                selected.toggleClass("active");
            }
        }
        var refElements = jQuery(".sidebar-ref", self.element);
        var moreTag = undefined;
        for (var i = 0; i < refElements.length; ++i) {
            var refElement = refElements[i];
            if (refElement.refName == refName) {
                jQuery(refElement).toggleClass("active");
                if (refElement.tagName == "LI") {
                    moreTag = null;
                } else if (moreTag !== null) {
                    moreTag = jQuery(".sidebar-more", refElement.section);
                }
            }
        }
        if (moreTag && moreTag.length) {
            moreTag.toggleClass("active");
        }
        self.mainView.historyView.update(refName);
    };

    self.addPopup = function(section, title, id, refs) {
        var popup = jQuery(  '<div class="modal fade" id="' + id + '" role="dialog">' +
                            '<div class="modal-dialog modal-sm">' +
                                '<div class="modal-content">' +
                                    '<div class="modal-header">' +
                                        '<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>' +
                                        '<h4 class="modal-title">' + title + '</h4>' +
                                    '</div>' +
                                    '<div class="modal-body"><div class="list-group"></div></div>' +
                                '</div>' +
                            '</div>' +
                        '</div>')[0];
        self.element.appendChild(popup);
        var popupContent = jQuery(".list-group", popup)[0];
        refs.forEach(function(ref) {
            var link = jQuery('<a class="list-group-item sidebar-ref">')[0];
            link.section = section;
            if (id == "local-branches-popup") {
                link.refName = ref.substr(2);
                if (ref[0] == "*") {
                    jQuery(link).addClass("branch-current");
                }
            } else {
                link.refName = ref;
            }
            jQuery(link).text(link.refName);
            popupContent.appendChild(link);
            jQuery(link).click(function (event) {
                jQuery(popup).modal('hide');
                self.selectRef(event.target.refName);
            });
        });
        return popup;
    };

    self.fetchSection = function(section, title, id, gitCommand) {
        webui.git(gitCommand, function(data) {
            var refs = webui.splitLines(data);
            if (id == "remote-branches") {
                refs = refs.map(function(ref) {
                    var end = ref.lastIndexOf(" -> ");
                    if (end == -1) {
                        return ref.substr(2);
                    } else {
                        return ref.substring(2, end);
                    }
                });
            }
            if (refs.length > 0) {
                var ul = jQuery("<ul>").appendTo(section)[0];
                refs = refs.sort(function(a, b) {
                    if (id != "local-branches") {
                        return -a.localeCompare(b);
                    } else if (a[0] == "*") {
                        return -1;
                    } else if (b[0] == "*") {
                        return 1;
                    } else {
                        return a.localeCompare(b);
                    }
                });

                var maxRefsCount = 5;
                if (id == "mounts") {
                    maxRefsCount = refs.length;
                    refs = refs.reverse();
                }
                for (var i = 0; i < refs.length && i < maxRefsCount; ++i) {
                    var ref = refs[i];
                    if (ref[2] == '(' && ref[ref.length - 1] == ')') {
                        // This is a '(detached from XXXXXX)'
                        var newref = ref.substring(ref.lastIndexOf(' ') + 1, ref.length - 1)
                        if (ref[0] == '*') {
                            ref = '* ' + newref;
                        } else {
                            ref = '  ' + newref;
                        }
                    }
                    var li = jQuery('<li class="sidebar-ref">').appendTo(ul)[0];
                    if (id == "local-branches") {
                        li.refName = ref.substr(2);
                        if (ref[0] == "*") {
                            jQuery(li).addClass("branch-current");
                        }
                    } else {
                        li.refName = ref;
                    }
                    jQuery(li).attr("title", li.refName);
                    jQuery(li).text(li.refName);
                    jQuery(li).click(function (event) {
                        if (id == "mounts") {
                            jQuery("*", self.element).removeClass("active");
                            filesElement.addClass("active");
                            self.mainView.filesView.update();
                            self.mainView.filesView.treeView.stack.push({ name: event.target.refName, object: '/~' + event.target.refName });
                            self.mainView.filesView.treeView.showTree();
                        } else {
                            self.selectRef(event.target.refName);
                        }
                    });
                }

                if (refs.length > maxRefsCount) {
                    var li = jQuery('<li class="sidebar-more">More ...</li>').appendTo(ul);
                    var popup = self.addPopup(section, title, id + "-popup", refs);
                    li.click(function() {
                        jQuery(popup).modal();
                    });
                }
            } else {
                jQuery(section).remove();
            }
        });
    };

    self.mainView = mainView;
    self.element = jQuery('<div id="sidebar">' +
                            '<div id="sidebar-content">' +
                                '<section id="sidebar-files">' +
                                '<h4><i class="fa fa-home"></i> Files</h4>' +
                                '</section>' +
                                '<section id="sidebar-workspace">' +
                                '<h4><i class="fa fa-briefcase"></i>Git Workspace</h4>' +
                                '</section>' +
                                '<section id="sidebar-local-branches">' +
                                '<h4><i class="fa fa-code-fork"></i> Local Branches</h4>' +
                                '</section>' +
                                '<section id="sidebar-remote-branches">' +
                                '<h4><i class="fa fa-globe"></i>Remote Branches</h4>' +
                                '</section>' +
                                '<section id="sidebar-tags">' +
                                '<h4><i class="fa fa-tags"></i>Tags</h4>' +
                                '</section>' +
                            '</div>' +
                        '</div>')[0];

    var workspaceElement = jQuery("#sidebar-workspace h4", self.element);
    workspaceElement.click(function (event) {
        jQuery("*", self.element).removeClass("active");
        workspaceElement.addClass("active");
        self.mainView.workspaceView.update([ "stage" ]);
    });

    var filesElement = jQuery("#sidebar-files h4", self.element);
    filesElement.click(function (event) {
        jQuery("*", self.element).removeClass("active");
        filesElement.addClass("active");
        self.mainView.filesView.update();
    });

    self.fetchSection(jQuery("#sidebar-files", self.element)[0], "Files", "mounts", [ "mounts" ]);
    self.fetchSection(jQuery("#sidebar-local-branches", self.element)[0], "Local Branches", "local-branches", [ "branch" ]);
    self.fetchSection(jQuery("#sidebar-remote-branches", self.element)[0], "Remote Branches", "remote-branches", [ "branch", "--remotes" ]);
    self.fetchSection(jQuery("#sidebar-tags", self.element)[0], "Tags", "tags", [ "tag" ]);
};

/*
 * == LogView =================================================================
 */
webui.LogView = function(historyView) {

    var self = this;

    self.update = function(ref) {
        jQuery(svg).empty();
        streams = []
        jQuery(content).empty();
        self.nextRef = ref;
        self.populate();
    };

    self.populate = function() {
        var maxCount = 1000;
        if (content.childElementCount > 0) {
            // The last node is the 'Show more commits placeholder'. Remove it.
            content.removeChild(content.lastElementChild);
        }
        var startAt = content.childElementCount;
        webui.git([ "log", "--date-order", "--pretty=raw", "--decorate=full", "--max-count=" + String(maxCount + 1), String(self.nextRef), "--" ], function(data) {
            var start = 0;
            var count = 0;
            self.nextRef = undefined;
            while (true) {
                var end = data.indexOf("\ncommit ", start);
                if (end != -1) {
                    var len = end - start;
                } else {
                    var len = undefined;
                }
                var entry = new Entry(self, data.substr(start, len));
                if (count < maxCount) {
                    content.appendChild(entry.element);
                    if (!self.lineHeight) {
                        self.lineHeight = Math.ceil(jQuery(entry.element).outerHeight() / 2) * 2;
                    }
                    entry.element.setAttribute("style", "height:" + self.lineHeight + "px");
                    if (!currentSelection) {
                        entry.select();
                    }
                } else {
                    self.nextRef = entry.commit;
                    break;
                }
                if (len == undefined) {
                    break;
                }
                start = end + 1;
                ++count;
            }
            svg.setAttribute("height", jQuery(content).outerHeight());
            svg.setAttribute("width", jQuery(content).outerWidth());
            if (self.nextRef != undefined) {
                var moreTag = jQuery('<a class="log-entry log-entry-more list-group-item">');
                jQuery('<a class="list-group-item-text">Show previous commits</a>').appendTo(moreTag[0]);
                moreTag.click(self.populate);
                moreTag.appendTo(content);
            }

            self.updateGraph(startAt);
        });
    };

    self.updateGraph = function(startAt) {
        // Draw the graph
        var currentY = (startAt + 0.5) * self.lineHeight;
        var maxLeft = 0;
        if (startAt == 0) {
            streamColor = 0;
        }
        for (var i = startAt; i < content.children.length; ++i) {
            var entry = content.children[i].model;
            if (!entry) {
                break;
            }
            var index = 0;
            entry.element.webuiLeft = streams.length;

            // Find streams to join
            var childCount = 0;
            var xOffset = 12;
            var removedStreams = 0;
            for (var j = 0; j < streams.length;) {
                var stream = streams[j];
                if (stream.sha1 == entry.commit) {
                    if (childCount == 0) {
                        // Replace the stream
                        stream.path.setAttribute("d", stream.path.cmds + currentY);
                        if (entry.parents.length == 0) {
                            streams.splice(j, 1);
                        } else {
                            stream.sha1 = entry.parents[0];
                        }
                        index = j;
                        ++j;
                    } else {
                        // Join the stream
                        var x = (index + 1) * xOffset;
                        stream.path.setAttribute("d", stream.path.cmds + (currentY - self.lineHeight / 2) + " L " + x + " " + currentY);
                        streams.splice(j, 1);
                        ++removedStreams;
                    }
                    ++childCount;
                } else {
                    if (removedStreams != 0) {
                        var x = (j + 1) * xOffset;
                        stream.path.setAttribute("d", stream.path.cmds + (currentY - self.lineHeight / 2) + " L " + x + " " + currentY);
                    }
                    ++j;
                }
            }

            // Add new streams
            for (var j = 0; j < entry.parents.length; ++j) {
                var parent = entry.parents[j];
                var x = (index + j + 1) * xOffset;
                if (j != 0 || streams.length == 0) {
                    var svgPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
                    ++streamColor
                    if (streamColor == webui.COLORS.length) {
                        streamColor = 0;
                    }
                    svgPath.setAttribute("style", "stroke:" + webui.COLORS[streamColor]);
                    var origX = (index + 1) * xOffset;
                    svgPath.cmds = "M " + origX + " " + currentY + " L " + x + " " + (currentY + self.lineHeight / 2) + " L " + x + " ";
                    svg.appendChild(svgPath);
                    var obj = {
                        sha1: parent,
                        path: svgPath,
                    };
                    streams.splice(index + j, 0, obj);
                }
            }
            for (var j = index + j; j < streams.length; ++j) {
                var stream = streams[j];
                var x = (j + 1) * xOffset;
                stream.path.cmds += (currentY - self.lineHeight / 2) + " L " + x + " " + currentY + " L " + x + " ";
            }

            var svgCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            svgCircle.setAttribute("cx", (index + 1) * xOffset);
            svgCircle.setAttribute("cy", currentY);
            svgCircle.setAttribute("r", 4);
            svg.appendChild(svgCircle);

            entry.element.webuiLeft = Math.max(entry.element.webuiLeft, streams.length);
            maxLeft = Math.max(maxLeft, entry.element.webuiLeft);
            // Debug log
            //console.log(entry.commit, entry.parents, jQuery.extend(true, [], streams));

            currentY += self.lineHeight;
        }
        for (var i = startAt; i < content.children.length; ++i) {
            var element = content.children[i];
            if (element.model) {
                var minLeft = Math.min(maxLeft, 3);
                var left = element ? Math.max(minLeft, element.webuiLeft) : minLeft;
                element.setAttribute("style", element.getAttribute("style") + ";padding-left:" + (left + 1) * xOffset + "px");
            }
        }
        for (var i = 0; i < streams.length; ++i) {
            var stream = streams[i];
            stream.path.setAttribute("d", stream.path.cmds + currentY);
        }
    }

    function Person(data) {
        var nameEnd = data.indexOf("<");
        this.name = data.substr(0, nameEnd - 1);
        var emailEnd = data.indexOf(">", nameEnd);
        this.email = data.substr(nameEnd + 1, emailEnd - nameEnd - 1);
        var dateEnd = data.indexOf(" ", emailEnd + 2);
        var secs = data.substr(emailEnd + 2, dateEnd - emailEnd - 2);
        this.date = new Date(0);
        this.date.setUTCSeconds(parseInt(secs));
    };

    function Entry(logView, data) {
        var self = this;

        self.abbrevCommitHash = function() {
            return self.commit.substr(0, 7);
        };

        self.abbrevMessage = function() {
            var end = self.message.indexOf("\n");
            if (end == -1) {
                return self.message
            } else {
                return self.message.substr(0, end);
            }
        };

        self.createElement = function() {
            self.element = jQuery('<a class="log-entry list-group-item">' +
                                '<header>' +
                                    '<h6></h6>' +
                                    '<span class="log-entry-date">' + self.author.date.toLocaleString() + '&nbsp;</span> ' +
                                    '<span class="badge">' + self.abbrevCommitHash() + '</span>' +
                                '</header>' +
                                '<p class="list-group-item-text"></p>' +
                             '</a>')[0];
            jQuery('<span>' + self.author.name + ' &lt;' + self.author.email + '&gt;</span>').appendTo(jQuery("h6", self.element));
            jQuery(".list-group-item-text", self.element)[0].appendChild(document.createTextNode(self.abbrevMessage()));
            if (self.refs) {
                var entryName = jQuery("h6", self.element);
                self.refs.forEach(function (ref) {
                    if (ref.indexOf("refs/remotes") == 0) {
                        ref = ref.substr(13);
                        var reftype = "danger";
                    } else if (ref.indexOf("refs/heads") == 0) {
                        ref = ref.substr(11);
                        var reftype = "success";
                    } else if (ref.indexOf("tag: refs/tags") == 0) {
                        ref = ref.substr(15);
                        var reftype = "info";
                    } else {
                        var reftype = "warning";
                    }
                    jQuery('<span>&nbsp;</span><span class="label label-' + reftype + '">' + ref + '</span>').insertAfter(entryName);
                });
            }
            self.element.model = self;
            var model = self;
            jQuery(self.element).click(function (event) {
                model.select();
            });
            return self.element;
        };

        self.select = function() {
            if (currentSelection != self) {
                if (currentSelection) {
                    jQuery(currentSelection.element).removeClass("active");
                }
                jQuery(self.element).addClass("active");
                currentSelection = self;
                logView.historyView.commitView.update(self);
            }
        };

        self.parents = [];
        self.message = ""

        data.split("\n").forEach(function(line) {
            if (line.indexOf("commit ") == 0) {
                self.commit = line.substr(7, 40);
                if (line.length > 47) {
                    self.refs = []
                    var s = line.lastIndexOf("(") + 1;
                    var e = line.lastIndexOf(")");
                    line.substr(s, e - s).split(", ").forEach(function(ref) {
                        self.refs.push(ref);
                    });
                }
            } else if (line.indexOf("parent ") == 0) {
                self.parents.push(line.substr(7));
            } else if (line.indexOf("tree ") == 0) {
                self.tree = line.substr(5);
            } else if (line.indexOf("author ") == 0) {
                self.author = new Person(line.substr(7));
            } else if (line.indexOf("committer ") == 0) {
                self.committer = new Person(line.substr(10));
            } else if (line.indexOf("    ") == 0) {
                self.message += line.substr(4) + "\n";
            }
        });

        self.message = self.message.trim();

        self.createElement();
    };

    self.historyView = historyView;
    self.element = jQuery('<div id="log-view" class="list-group"><svg xmlns="http://www.w3.org/2000/svg"></svg><div></div></div>')[0];
    var svg = self.element.children[0];
    var content = self.element.children[1];
    var currentSelection = null;
    var lineHeight = null;
    var streams = [];
    var streamColor = 0;
};

/*
 * == DiffView ================================================================
 */
webui.DiffView = function(sideBySide, hunkSelectionAllowed, parent) {

    var self = this;

    self.update = function(cmd, diffOpts, file, mode) {
        gitApplyType = mode;
        jQuery(".diff-stage", self.element).attr("style", "display:none");
        jQuery(".diff-cancel", self.element).attr("style", "display:none");
        jQuery(".diff-unstage", self.element).attr("style", "display:none");
        if (cmd) {
            self.gitCmd = cmd;
            self.gitDiffOpts = diffOpts;
            if (file != self.gitFile) {
                left.scrollTop = 0;
                left.scrollLeft = 0;
                right.scrollTop = 0;
                right.scrollLeft = 0;
                left.webuiPrevScrollTop = 0;
                left.webuiPrevScrollLeft = 0;
                right.webuiPrevScrollTop = 0;
                right.webuiPrevScrollLeft = 0;
            }
            self.gitFile = file;
        }
        if (self.gitCmd) {
            var fullCmd = self.gitCmd;
            if (self.complete) {
                fullCmd.push("--unified=999999999");
            } else {
                fullCmd.push("--unified=" + self.context.toString());
            }
            if (self.ignoreWhitespace) {
                fullCmd.push("--ignore-all-space");
                fullCmd.push("--ignore-blank-lines");
            }
            if (self.gitDiffOpts) {
                fullCmd = fullCmd.concat(self.gitDiffOpts);
            }
            if (self.gitFile) {
                fullCmd.push("--");
                fullCmd.push(self.gitFile);
            }
            webui.git(fullCmd, function(diff) {
                self.refresh(diff);
            });
        } else {
            self.refresh("");
        }
    };

    self.refresh = function(diff) {
        self.currentDiff = diff;
        self.diffHeader = "";
        jQuery("span", self.element).text('Context: ' + self.context);
        if (sideBySide) {
            var diffLines = diff.split("\n");
            self.updateSplitView(leftLines, diffLines, '-');
            self.updateSplitView(rightLines, diffLines, '+');
        } else {
            self.updateSimpleView(singleLines, diff);
        }
    }

    self.updateSimpleView = function(view, diff) {
        jQuery(view).empty();

        var context = { inHeader: true };
        var diffLines = diff.split("\n");
        for (var i = 0; i < diffLines.length; ++i) {
            var line = diffLines[i];
            context = self.addDiffLine(view, line, context);
        }
    }

    self.updateSplitView = function(view, diffLines, operation) {
        jQuery(view).empty();

        var context = { inHeader: true,
                        addedLines: [],
                        removedLines: [],
                      };
        for (var i = 0; i < diffLines.length; ++i) {
            var line = diffLines[i];
            var c = line[0];
            if (c == '+') {
                context.addedLines.push(line);
                if (context.inHeader) {
                    context.diffHeader += line + '\n';
                }
            } else if (c == '-') {
                context.removedLines.push(line);
                if (context.inHeader) {
                    context.diffHeader += line + '\n';
                }
            } else {
                context = self.flushAddedRemovedLines(view, operation, context);
                context.addedLines = [];
                context.removedLines = [];
                context = self.addDiffLine(view, line, context);
                if (c == 'd') {
                    context.diffHeader = '';
                }
            }
        }
        self.flushAddedRemovedLines(view, operation, context);
        view.parentElement.scrollTop = view.parentElement.webuiPrevScrollTop;
    }

    self.flushAddedRemovedLines = function(view, operation, context) {
        if (operation == '+') {
            var lines = context.addedLines;
            var offset = context.removedLines.length - context.addedLines.length;
        } else {
            var lines = context.removedLines;
            var offset = context.addedLines.length - context.removedLines.length;
        }
        lines.forEach(function(line) {
            context = self.addDiffLine(view, line, context);
        });
        if (offset > 0) {
            for (var i = 0; i < offset; ++i) {
                var pre = jQuery('<pre class="diff-view-line diff-line-phantom">').appendTo(view)[0];
                pre.appendChild(document.createTextNode(" "));
            }
        }
        return context;
    }

    self.addDiffLine = function(view, line, context) {
        var c = line[0];
        var pre = jQuery('<pre class="diff-view-line">').appendTo(view)[0];
        pre.appendChild(document.createTextNode(line));
        if (c == '+') {
            jQuery(pre).addClass("diff-line-add");
        } else if (c == '-') {
            jQuery(pre).addClass("diff-line-del");
        } else if (c == '@') {
            jQuery(pre).addClass("diff-line-offset");
            pre.webuiActive = false;
            context.inHeader = false;
        } else if (c == 'd') {
            context.inHeader = true;
        }
        if (context.inHeader) {
            jQuery(pre).addClass("diff-line-header");
            if (c == 'd') jQuery(pre).addClass("diff-section-start");
        }
        return context;
    }

    self.createSelectionPatch = function (reverse) {
        var patch = "";
        // First create the header
        for (var l = 0; l < leftLines.childElementCount; ++l) {
            var line = leftLines.children[l].textContent;
            if (line[0] == "@") {
                break;
            } else {
                patch += line + "\n";
            }
        }
        patch += rightLines.children[l - 1].textContent + "\n";
        // Then build the patch itself
        var refLineNo = 0;
        var patchOffset = 0;
        var hunkAddedLines = [];
        var hunkRemovedLines = [];
        for (; l < leftLines.childElementCount; ++l) {
            var leftElt = leftLines.children[l];
            var leftLine = leftElt.textContent;
            var leftCmd = leftLine[0];

            if (leftCmd == "@" || (leftCmd == " " && !jQuery(leftElt).hasClass("diff-line-phantom"))) {
                if (hunkAddedLines.length != 0 || hunkRemovedLines.length != 0) {
                    patch += self.flushSelectionPatch(hunkAddedLines, hunkRemovedLines, refLineNo, patchOffset);
                    refLineNo += hunkRemovedLines.length
                    patchOffset += hunkAddedLines.length - hunkRemovedLines.length;
                    var hunkAddedLines = [];
                    var hunkRemovedLines = [];
                }
                if (leftCmd == "@") {
                    var splittedContext = leftLine.split(" ");
                    if (!reverse) {
                        refLineNo = Math.abs(splittedContext[1].split(",")[0]);
                    } else {
                        refLineNo = Math.abs(splittedContext[2].split(",")[0]);
                    }
                } else {
                    ++refLineNo;
                }
            } else if (leftCmd == "-" || jQuery(leftElt).hasClass("diff-line-phantom")) {
                if (leftCmd == "-") {
                    if (jQuery(leftElt).hasClass("active")) {
                        if (!reverse) {
                            hunkRemovedLines.push(leftLine);
                        } else {
                            hunkAddedLines.push(self.reverseLine(leftLine));
                        }
                    } else if (!reverse) {
                        ++refLineNo;
                    }
                }
                var rightElt = rightLines.children[l];
                if (!jQuery(rightElt).hasClass("diff-line-phantom")) {
                    if (jQuery(rightElt).hasClass("active")) {
                        if (!reverse) {
                            hunkAddedLines.push(rightElt.textContent);
                        } else {
                            hunkRemovedLines.push(self.reverseLine(rightElt.textContent));
                        }
                    } else if (reverse) {
                        ++refLineNo;
                    }
                }
            }
        }
        if (hunkAddedLines.length != 0 || hunkRemovedLines.length != 0) {
            patch += self.flushSelectionPatch(hunkAddedLines, hunkRemovedLines, refLineNo, patchOffset);
        }
        return patch;
    }

    self.flushSelectionPatch = function(hunkAddedLines, hunkRemovedLines, refLineNo, patchOffset) {
        var patch = "@@ -" + refLineNo + "," + hunkRemovedLines.length +" +" + (refLineNo + patchOffset) + "," + hunkAddedLines.length + " @@\n";
        hunkRemovedLines.forEach(function (line) { patch += line + "\n" });
        hunkAddedLines.forEach(function (line) { patch += line + "\n" });
        return patch;
    }

    self.reverseLine = function(line) {
        switch (line[0]) {
            case '-':
                return '+' + line.substr(1);
            case '+':
                return '-' + line.substr(1);
                break;
            default:
                return line;
                break;
        }
    }

    self.diffViewScrolled = function(event) {
        if (event.target == left) {
            var current = left;
            var other = right;
        } else {
            var current = right;
            var other = left;
        }
        if (current.webuiPrevScrollTop != current.scrollTop) {
            // Vertical scrolling
            other.scrollTop = current.scrollTop;
            other.webuiPrevScrollTop = current.webuiPrevScrollTop = current.scrollTop;
        } else if (current.webuiPrevScrollLeft != current.scrollLeft) {
            // Horizontal scrolling
            other.scrollLeft = current.scrollLeft;
            other.webuiPrevScrollLeft = current.webuiPrevScrollLeft = current.scrollLeft;
        }
    }

    self.addContext = function() {
        self.context += 3;
        self.update();
    }

    self.removeContext = function() {
        if (self.context > 3) {
            self.context -= 3;
            self.update();
        }
    }

    self.allContext = function() {
        self.complete = !self.complete;
        self.update();
    }

    self.toggleIgnoreWhitespace = function() {
        self.ignoreWhitespace = !self.ignoreWhitespace;
        self.update();
    }

    self.handleClick = function(event) {
        var lineElt = event.target;
        while (lineElt && !jQuery(lineElt).hasClass("diff-view-line")) {
            lineElt = lineElt.parentElement;
        }
        if (!lineElt) {
            return;
        }
        var diffLine = lineElt.textContent;
        var cmd = diffLine[0];
        if (cmd == "+" || cmd == "-") {
            jQuery(lineElt).toggleClass("active");
        } else if (cmd == "@") {
            lineElt.webuiActive = !lineElt.webuiActive;
            for (var elt = lineElt.nextElementSibling; elt; elt = elt.nextElementSibling) {
                cmd = elt.textContent[0];
                if (cmd == "+" || cmd == "-") {
                    jQuery(elt).toggleClass("active", lineElt.webuiActive);
                } else if (cmd == "@") {
                    break;
                }
            }
        }

        var isActive = false
        var lineContainers = [leftLines, rightLines];
        for (var i = 0; i < lineContainers.length; ++i) {
            var lineContainer = lineContainers[i];
            for (var j = 0; j < lineContainer.childElementCount; ++j) {
                var elt = lineContainer.children[j];
                if (jQuery(elt).hasClass("active")) {
                    isActive = true;
                    break;
                }
            }
        }
        if (isActive) {
            if (gitApplyType == "stage") {
                jQuery(".diff-stage", self.element).removeAttr("style");
                jQuery(".diff-cancel", self.element).removeAttr("style");
                jQuery(".diff-unstage", self.element).attr("style", "display:none");
            } else {
                jQuery(".diff-stage", self.element).attr("style", "display:none");
                jQuery(".diff-cancel", self.element).attr("style", "display:none");
                jQuery(".diff-unstage", self.element).removeAttr("style");
            }
        } else {
            jQuery(".diff-stage", self.element).attr("style", "display:none");
            jQuery(".diff-cancel", self.element).attr("style", "display:none");
            jQuery(".diff-unstage", self.element).attr("style", "display:none");
        }
    }

    self.applySelection = function(reverse, cached) {
        var patch = self.createSelectionPatch(reverse);
        var cmd = [ "apply", "--unidiff-zero" ];
        if (cached) {
            cmd.push("--cached");
        }
        webui.git(cmd, patch, function (data) {
            parent.update();
        });
    }

    self.switchToExploreView = function() {
        if (! self.currentDiff) {
            return;
        }
        var mainView = parent.historyView.mainView;
        var commitExplorerView = new webui.CommitExplorerView(mainView, self.currentDiff);
        commitExplorerView.show();
    };

    var html = '<div class="diff-view-container panel panel-default">';
    if (! (parent instanceof webui.CommitExplorerView)) {
        html +=
            '<div class="panel-heading btn-toolbar" role="toolbar">' +
                '<button type="button" class="btn btn-sm btn-default diff-ignore-whitespace" data-toggle="button">Ignore Whitespace</button>' +
                '<button type="button" class="btn btn-sm btn-default diff-context-all" data-toggle="button">Complete file</button>' +
                '<div class="btn-group btn-group-sm">' +
                    '<span></span>&nbsp;' +
                    '<button type="button" class="btn btn-default diff-context-remove">-</button>' +
                    '<button type="button" class="btn btn-default diff-context-add">+</button>' +
                '</div>' +
                '<div class="btn-group btn-group-sm diff-selection-buttons">' +
                    '<button type="button" class="btn btn-default diff-stage" style="display:none">Stage</button>' +
                    '<button type="button" class="btn btn-default diff-cancel" style="display:none">Cancel</button>' +
                    '<button type="button" class="btn btn-default diff-unstage" style="display:none">Unstage</button>' +
                '</div>' +
                (sideBySide ? '' : '<button type="button"  class="btn btn-sm btn-default diff-explore">Explore</button>') +
            '</div>';
    }
    html += '<div class="panel-body"></div></div>'
    self.element = jQuery(html)[0];
    var panelBody = jQuery(".panel-body", self.element)[0];
    if (sideBySide) {
        var left = jQuery('<div class="diff-view"><div class="diff-view-lines"></div></div>')[0];
        panelBody.appendChild(left);
        var leftLines = left.firstChild;
        jQuery(left).scroll(self.diffViewScrolled);
        left.webuiPrevScrollTop = left.scrollTop;
        left.webuiPrevScrollLeft = left.scrollLeft;
        var right = jQuery('<div class="diff-view"><div class="diff-view-lines"></div></div>')[0];
        panelBody.appendChild(right);
        var rightLines = right.firstChild;
        jQuery(right).scroll(self.diffViewScrolled);
        right.webuiPrevScrollTop = right.scrollTop;
        right.webuiPrevScrollLeft = right.scrollLeft;
        if (hunkSelectionAllowed) {
            jQuery(left).click(self.handleClick);
            jQuery(right).click(self.handleClick);
        }
    } else {
        var single = jQuery('<div class="diff-view"><div class="diff-view-lines"></div></div>')[0];
        panelBody.appendChild(single);
        var singleLines = single.firstChild;
    }

    jQuery(".diff-context-remove", self.element).click(self.removeContext);
    jQuery(".diff-context-add", self.element).click(self.addContext);
    jQuery(".diff-context-all", self.element).click(self.allContext);
    jQuery(".diff-ignore-whitespace", self.element).click(self.toggleIgnoreWhitespace);

    jQuery(".diff-stage", self.element).click(function() { self.applySelection(false, true); });
    jQuery(".diff-cancel", self.element).click(function() { self.applySelection(true, false); });
    jQuery(".diff-unstage", self.element).click(function() { self.applySelection(true, true); });

    jQuery(".diff-explore", self.element).click(function() { self.switchToExploreView(); });

    self.context = 3;
    self.complete = false;
    self.ignoreWhitespace = false;
    var gitApplyType = "stage";
};

/*
 * == TreeView ================================================================
 */
webui.TreeView = function(commitView) {

    var self = this;

    function Entry(line) {

        var self = this;

        // https://en.wikipedia.org/wiki/Kilobyte
        self.formatedSize = function(size) {
            if (isNaN(self.size)) {
                return "";
            }
            if (self.size < 1000) {
                return self.size.toString() + " B";
            } else if (self.size < 1000000) {
                return (self.size / 1000).toFixed(2) + " kB";
            } else if (self.size < 1000000000) {
                return (self.size / 1000000).toFixed(2) + " MB";
            } else {
                return (self.size / 1000000000).toFixed(2) + " GB";
            }
        };

        self.isSymbolicLink = function() {
            return (self.mode & 120000) == 120000; // S_IFLNK
        }

        var end = line.indexOf(" ");
        self.mode = parseInt(line.substr(0, end));
        var start = end + 1;
        var end = line.indexOf(" ", start);
        self.type = line.substr(start, end - start);
        start = end + 1;
        var end = line.indexOf(" ", start);
        self.object = line.substr(start, end - start);
        start = end + 1;
        var end = line.indexOf("\t", start);
        self.size = parseInt(line.substr(start, end - start).trim());
        start = end + 1;
        self.name = line.substr(start);
    }

    self.update = function(treeRef) {
        self.stack = [ { name: webui.repo, object: treeRef } ];
        self.showTree();
    }

    self.createBreadcrumb = function() {
        jQuery(breadcrumb).empty();
        for (var i = 0; i < self.stack.length; ++i) {
            var last = i == self.stack.length - 1;
            var name = self.stack[i].name;
            if (!last) {
                name = '<a href="#">' + name + '</a>';
            }
            var li = jQuery('<li>' + name + '</li>');
            li.appendTo(breadcrumb);
            if (!last) {
                li.click(self.breadcrumbClicked);
            } else {
                li.addClass("active");
            }
        }
    }

    self.breadcrumbClicked = function(event) {
        var to = webui.getNodeIndex(event.target.parentElement);
        self.stack = self.stack.slice(0, to + 1);
        self.showTree();
    }

    self.showTree = function() {
        jQuery(self.element.lastElementChild).remove();
        var treeViewTreeContent = jQuery('<div id="tree-view-tree-content" class="list-group">')[0];
        self.element.appendChild(treeViewTreeContent);
        self.createBreadcrumb();
        var treeRef = self.stack[self.stack.length - 1].object;
        var parentTreeRef = self.stack.length > 1 ? self.stack[self.stack.length - 2].object : undefined;
        var cmd = (treeRef === undefined || treeRef.startsWith('/')) ? 'ls-local' : 'ls-tree';
        webui.git([ cmd, "-l", treeRef ], function(data) {
            var blobs = [];
            var trees = [];
            if (parentTreeRef || (treeRef !== undefined && treeRef.startsWith('/')) ) {
                var elt =   jQuery('<a href="#" class="list-group-item">' +
                                '<span class="tree-item-tree">..</span> ' +
                                '<span></span> ' +
                                '<span></span> ' +
                            '</a>');
                elt.click(function() {
                    self.stack.pop();
                    self.showTree();
                });
                elt.appendTo(treeViewTreeContent);
            }
            webui.splitLines(data).forEach(function(line) {
                var entry = new Entry(line);
                var size = entry.formatedSize()
                var download = (entry.type == "tree") ? '' : ' <i class="fa fa-download" aria-hidden="true"></i>';
                var mtime = entry.object.split('#')[1];
                if (mtime === undefined) {
                    mtime = '';
                } else {
                    mtime = mtime.replace('T', ' ');
                }
                var elt = jQuery('<span class="list-group-item">' +
                                 '<a class="name" href="#">' + entry.name + '</a> ' +
                                 '<span class="mtime">' + mtime + '</span>' +
                                 '<span class="size">' + size + '</span>&nbsp;' +
                                 '<a class="download" href="#">' + download + '</a>' +
                                 '</span>')[0];
                elt.model = entry;
                var nameElt = jQuery("a", elt)[0];
                jQuery(nameElt).addClass("tree-item-" + entry.type);
                if (entry.isSymbolicLink()) {
                    jQuery(nameElt).addClass("tree-item-symlink");
                }
                if (entry.type == "tree") {
                    trees.push(elt);
                    jQuery(elt).children('.name').click(function(t) {
                        self.stack.push({ name: elt.model.name, object: elt.model.object});
                        self.showTree();
                    });
                } else {
                    blobs.push(elt);
                    jQuery(elt).children('.name').click(function(t) {
                        self.stack.push({ name: elt.model.name, object: elt.model.object});
                        self.showBlob();
                    });
                    jQuery(elt).children('.download').click(function(t) {
                        if (elt.model.object[0] == '/') { // file
                            window.location.href = '/code_editor/download' + elt.model.object;
                        } else { // blob
                            window.location.href = '/code_editor/download/~git/' + elt.model.object + '/' + elt.model.name;
                        }
                    });
                }
            });
            var compare = function(a, b) {
                return a.model.name.toLowerCase().localeCompare(b.model.name.toLowerCase());
            }
            blobs.sort(compare);
            trees.sort(compare);
            trees.forEach(function (elt) {
                treeViewTreeContent.appendChild(elt);
            });
            blobs.forEach(function (elt) {
                treeViewTreeContent.appendChild(elt);
            });
        });
    }

    self.showBlob = function(blobRef) {
        self.createBreadcrumb();
        jQuery(self.element.lastElementChild).remove();
        var object = self.stack[self.stack.length - 1].object;
        if (object[0] == '/') {
            jQuery('<div id="tree-view-blob-content">' +
                   '<iframe src="/code_editor/editor' + object + '"></iframe>' +
                   '</div>').appendTo(self.element);
        } else {
            // jQuery('<div id="tree-view-blob-content">' +
            //        '<iframe src="/code_editor/repo/' + object + '"></iframe>' +
            //        '</div>').appendTo(self.element);
            jQuery('<div id="tree-view-blob-content">' +
                '<textarea></textarea>' +
                '</div>').appendTo(self.element);

            var textarea = jQuery('#tree-view-blob-content textarea')[0];
            var editor = CodeMirror.fromTextArea(textarea, {
                readOnly: true,
                lineNumbers: true,
                mode: 'python',
                foldGutter: true,
                gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"]
            });
            var client = new XMLHttpRequest();
            client.open('GET', '/code_editor/repo/' + object);
            client.onreadystatechange = function() {
                editor.setValue(client.responseText);
                editor.refresh();
            }
            client.send();
        }
    }

    self.element = jQuery('<div id="tree-view">')[0];
    var breadcrumb = jQuery('<ol class="breadcrumb">')[0];
    self.element.appendChild(breadcrumb);
    self.element.appendChild(jQuery('<div id="tree-view-tree-content">')[0]);
    var stack;
}

/*
 * == CommitExplorerView =============================================================
 */
webui.CommitExplorerView = function(mainView, diff) {

    var self = this;
    var diffLines = diff.split("\n");
    var diffHeaderLines = [];
    var diffSections = [];
    var currentSection, line, c, lineMatch;

    self.buildDiffSections = function(diff) {
        var visitorState = 'header';

        for (var i = 0; i < diffLines.length; i++) {
            line = diffLines[i];
            c = line[0];

            switch(visitorState) {
            case 'header':
                if (c == 'd') {
                    visitorState = 'sectionHeader';
                    i -= 1;
                } else {
                    diffHeaderLines.push(line)
                }
                break;
            case 'sectionHeader':
                lineMatch = line.match(/^diff --git a\/(.*) b\/(.*)jQuery/)
                currentSection = {
                    leftName: lineMatch[1],
                    rightName: lineMatch[2],
                    lines: []
                };
                diffSections.push(currentSection);
                visitorState = 'sectionContent';
                break;
            case 'sectionContent':
                if (c == 'd') {
                    visitorState = 'sectionHeader';
                    i -= 1;
                } else {
                    currentSection.lines.push(line);
                }
            }
        }
    }

    self.show = function() {
        mainView.switchTo(self.element);
    };

    self.displayDiffForSection = function(idx) {
        self.diffView.refresh(diffSections[idx].lines.join("\n"));
    };

    self.element = jQuery(    '<div id="commit-explorer-view">'+
                             '<div id="commit-explorer-diff-view"></div>'+
                             '<div id="commit-explorer-navigator-view"></div>'+
                         '</div>')[0];

    var commitExplorerDiffView = jQuery('#commit-explorer-diff-view', self.element)[0];
    var commitExplorerNavigatorView = jQuery('#commit-explorer-navigator-view', self.element)[0];

    self.buildDiffSections(diff);

    self.diffView = new webui.DiffView(true, false, self);
    self.fileListView = new webui.FileListView(self, diffSections);
    self.commitHeaderView = new webui.CommitHeaderView(self, diffHeaderLines.join("\n"));

    self.displayDiffForSection(0);

    commitExplorerDiffView.appendChild(self.diffView.element);
    commitExplorerNavigatorView.appendChild(self.fileListView.element);
    commitExplorerNavigatorView.appendChild(self.commitHeaderView.element);

}

webui.FileListView = function(commitExplorerView, files){
    var self = this;

    self.fileSelected = function(event) {
        var index = 0;
        var sibling = event.target.previousElementSibling;
        while (sibling) {
            sibling = sibling.previousElementSibling;
            ++index;
        }
        jQuery(".active", rightContainer).removeClass("active");
        jQuery(".active", leftContainer).removeClass("active");
        jQuery(rightContainer.children[index]).toggleClass("active");
        jQuery(leftContainer.children[index]).toggleClass("active");
        commitExplorerView.displayDiffForSection(index);
    };

    self.buildLine = function(label, parent) {
        var element = jQuery('<a class="list-group-item">' + label + '</a>')[0];
        jQuery(element).click(self.fileSelected)
        parent.appendChild(element);
    }

    self.viewScrolled = function(event) {
        if (event.target == rightScrollView) {
            var current = rightScrollView;
            var other = leftScrollView;
        } else {
            var current = leftScrollView;
            var other = rightScrollView;
        }
        other.scrollTop = current.scrollTop;
    }

    self.element = jQuery(   '<div class="file-list-view panel panel-default">' +
                            '<div class="panel-heading">' +
                                '<h5> Files </h5>' +
                            '</div>' +
                            '<div class="file-list-container">' +
                                '<div class="file-list-left-container">' +
                                    '<div class="list-group"></div>' +
                                '</div>' +
                                '<div class="file-list-right-container">' +
                                    '<div class="list-group"></div>' +
                                '</div>' +
                            '</div>' +
                         '</div>')[0];

    var rightScrollView = jQuery(".file-list-right-container", self.element)[0];
    var rightContainer =  jQuery(".list-group", rightScrollView)[0];
    var leftScrollView = jQuery(".file-list-left-container", self.element)[0];
    var leftContainer =  jQuery(".list-group", leftScrollView)[0];

    for (var i = 0; i < files.length; ++i) {
        var lineData = files[i];
        self.buildLine(lineData.rightName, rightContainer);
        self.buildLine(lineData.leftName, leftContainer);
    }
    jQuery(rightScrollView).scroll(self.viewScrolled);
    jQuery(leftScrollView).scroll(self.viewScrolled);
}

/*
 * == CommitHeaderView ==============================================================
 */
webui.CommitHeaderView = function(commitExplorerView, header) {
    var self = this;
    self.element = jQuery('<div class="panel panel-default">' +
                         '<div class="panel-heading">' +
                             '<h5> Commit Details </h5>' +
                         '</div>' +
                         '<div class="panel-body">' + header.split("\n").join("<br>") + '</div>' +
                     '</div>')[0];
}

/*
 * == CommitView ==============================================================
 */
webui.CommitView = function(historyView) {

    var self = this;

    self.update = function(entry) {
        if (currentCommit == entry.commit) {
            // We already display the right data. No need to update.
            return;

        }
        currentCommit = entry.commit;
        self.showDiff();
        buttonBox.select(0);
        diffView.update([ "show" ], [entry.commit]);
        treeView.update(entry.tree);
    };

    self.showDiff = function() {
        webui.detachChildren(commitViewContent);
        commitViewContent.appendChild(diffView.element);
    };

    self.showTree = function() {
        webui.detachChildren(commitViewContent);
        commitViewContent.appendChild(treeView.element);
    };

    self.historyView = historyView;
    var currentCommit = null;
    self.element = jQuery('<div id="commit-view">')[0];
    var commitViewHeader = jQuery('<div id="commit-view-header">')[0];
    self.element.appendChild(commitViewHeader);
    var buttonBox = new webui.TabBox([["Commit", self.showDiff], ["Tree", self.showTree]]);
    commitViewHeader.appendChild(buttonBox.element);
    var commitViewContent = jQuery('<div id="commit-view-content">')[0];
    self.element.appendChild(commitViewContent);
    var diffView = new webui.DiffView(false, false, self);
    var treeView = new webui.TreeView(self);
};

/*
 * == HistoryView =============================================================
 */
webui.HistoryView = function(mainView) {

    var self = this;

    self.show = function() {
        mainView.switchTo(self.element);
    };

    self.update = function(ref) {
        self.show();
        self.logView.update(ref);
    };

    self.element = jQuery('<div id="history-view">')[0];
    self.logView = new webui.LogView(self);
    self.element.appendChild(self.logView.element);
    self.commitView = new webui.CommitView(self);
    self.element.appendChild(self.commitView.element);
    self.mainView = mainView;
};

/*
 * == WorkspaceView ===========================================================
 */
webui.WorkspaceView = function(mainView) {

    var self = this;

    self.show = function() {
        mainView.switchTo(self.element);
    };

    self.update = function(mode) {
        self.show();
        self.workingCopyView.update();
        self.stagingAreaView.update();
        self.commitMessageView.update();
        if (self.workingCopyView.getSelectedItemsCount() + self.stagingAreaView.getSelectedItemsCount() == 0) {
            self.diffView.update(undefined, undefined, undefined, mode);
        }
    };

    self.element = jQuery('<div id="workspace-view">' +
                          '<div id="workspace-diff-view"></div>' +
                          '<div id="workspace-editor"></div>' +
                          '</div>')[0];
    var workspaceDiffView = jQuery("#workspace-diff-view", self.element)[0];
    self.diffView = new webui.DiffView(true, true, self);
    workspaceDiffView.appendChild(self.diffView.element);
    var workspaceEditor = jQuery("#workspace-editor", self.element)[0];
    self.workingCopyView = new webui.ChangedFilesView(self, "working-copy", "Working Copy");
    workspaceEditor.appendChild(self.workingCopyView.element);
    self.commitMessageView = new webui.CommitMessageView(self);
    workspaceEditor.appendChild(self.commitMessageView.element);
    self.stagingAreaView = new webui.ChangedFilesView(self, "staging-area", "Staging Area");
    workspaceEditor.appendChild(self.stagingAreaView.element);
};

/*
 * == FilesView ===========================================================
 */
webui.FilesView = function(mainView) {

    var self = this;

    self.show = function() {
        mainView.switchTo(self.element);
    };

    self.update = function() {
        self.show();
        self.treeView.update();
    };

    self.element = jQuery('<div id="workspace-view">' +
                          '<div id="workspace-editor"></div>' +
                          '</div>')[0];
    var workspaceEditor = jQuery("#workspace-editor", self.element)[0];
    self.treeView = new webui.TreeView(self);
    workspaceEditor.appendChild(self.treeView.element);
};

/*
 * == ChangedFilesView ========================================================
 */
webui.ChangedFilesView = function(workspaceView, type, label) {

    var self = this;

    self.update = function() {
        jQuery(fileList).empty()
        var col = type == "working-copy" ? 1 : 0;
        webui.git([ "status", "--porcelain" ], function(data) {
            self.filesCount = 0;
            webui.splitLines(data).forEach(function(line) {
                var status = line[col];
                if (col == 0 && status != " " && status != "?" || col == 1 && status != " ") {
                    ++self.filesCount;
                    var item = jQuery('<a class="list-group-item">').appendTo(fileList)[0];
                    item.status = status;
                    line = line.substr(3);
                    var splitted = line.split(" -> ");
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
                var selectedNode = fileList.children[selectedIndex];
                jQuery(selectedNode).addClass("active");
                self.refreshDiff(selectedNode);
            }
            fileListContainer.scrollTop = prevScrollTop;
        });
    };

    self.select = function(event) {
        var clicked = event.target;

        if (event.shiftKey && selectedIndex !== null) {
            var clickedIndex = webui.getNodeIndex(clicked);
            if (clickedIndex < selectedIndex) {
                var from = clickedIndex;
                var to = selectedIndex;
            } else {
                var from = selectedIndex;
                var to = clickedIndex;
            }
            for (var i = from; i <= to; ++i) {
                jQuery(fileList.children[i]).addClass("active");
            }
            selectedIndex = clickedIndex;
        } else if (event.ctrlKey) {
            jQuery(clicked).toggleClass("active");
            selectedIndex = webui.getNodeIndex(clicked);
        } else {
            for (var i = 0; i < fileList.childElementCount; ++i) {
                jQuery(fileList.children[i]).removeClass("active");
            }
            jQuery(clicked).addClass("active");
            selectedIndex = webui.getNodeIndex(clicked);
        }
        if (type == "working-copy") {
            workspaceView.stagingAreaView.unselect();
        } else {
            workspaceView.workingCopyView.unselect();
        }
        self.refreshDiff(clicked);
    };

    self.refreshDiff = function(element) {
        var cmd = [ "diff" ];
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
        var files = [];
        for (var i = 0; i < fileList.childElementCount; ++i) {
            var child = fileList.children[i];
            var included = including == undefined || including.indexOf(child.status) != -1;
            var excluded = excluding != undefined && excluding.indexOf(child.status) != -1;
            if (jQuery(child).hasClass("active") && included && !excluded) {
                files.push(child.model);
            }
        }
        return files;
    }

    self.process = function() {
        prevScrollTop = fileListContainer.scrollTop;
        var files = self.getFileList(undefined, "D");
        var rmFiles = self.getFileList("D");
        if (files.length != 0) {
            var cmd = type == "working-copy" ? ["add"] : ["reset"];
            cmd.push('--');
            webui.git(cmd.concat(files), function(data) {
                if (rmFiles.length != 0) {
                    var cmd = [ 'rm', '--'];
                    webui.git(cmd.concat(rmFiles), function(data) {
                        workspaceView.update(type == "working-copy" ? ["stage"] : ["unstage"]);
                    });
                } else {
                    workspaceView.update(type == "working-copy" ? ["stage"] : ["unstage"]);
                }
            });
        } else if (rmFiles.length != 0) {
            var cmd = type == "working-copy" ? ["rm"] : ["reset"];
            cmd.push('--')
            webui.git(cmd.concat(rmFiles), function(data) {
                workspaceView.update(type == "working-copy" ? ["stage"] : ["unstage"]);
            });
        }
    };

    self.cancel = function() {
        prevScrollTop = fileListContainer.scrollTop;
        var files = self.getFileList();
        if (files.length != 0) {
            var cmd = 'checkout'
            webui.git(cmd.concat(files), function(data) {
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
    if (type == "working-copy") {
        var buttons = [{ name: "Stage", callback: self.process }, { name: "Cancel", callback: self.cancel }];
    } else {
        var buttons = [{ name: "Unstage", callback: self.process }];
    }
    var btnGroup = jQuery(".btn-group", self.element);
    buttons.forEach(function (btnData) {
        var btn = jQuery('<button type="button" class="btn btn-default">' + btnData.name + '</button>')
        btn.appendTo(btnGroup);
        btn.click(btnData.callback);
    });
    var fileListContainer = jQuery(".file-list-container", self.element)[0];
    var prevScrollTop = fileListContainer.scrollTop;
    var fileList = jQuery(".list-group", fileListContainer)[0];
    var selectedIndex = null;

    self.filesCount = 0;
};

/*
 * == CommitMessageView =======================================================
 */
webui.CommitMessageView = function(workspaceView) {

    var self = this;

    self.onAmend = function() {
        if (!amend.hasClass("active") && textArea.value.length == 0) {
            webui.git([ "log", "--pretty=format:%B", "-n", "1" ], function(data) {
                textArea.value = data;
            });
        }
    };

    self.onCommit = function() {
        if (workspaceView.stagingAreaView.filesCount == 0 && !amend.hasClass("active")) {
            webui.showError("No files staged for commit");
        } else if (textArea.value.length == 0) {
            webui.showError("Enter a commit message first");
        } else {
            var cmd = [ "commit" ];
            if (amend.hasClass("active")) {
                cmd.push("--amend");
            }
            cmd.push("-m");
            cmd.push(textArea.value)
            webui.git(cmd, function(data) {
                textArea.value = "";
                workspaceView.update(["stage"]);
                amend.removeClass("active");
            });
        }
    }

    self.update = function() {
    }

    self.element = jQuery(   '<div id="commit-message-view" class="panel panel-default">' +
                            '<div class="panel-heading">' +
                                '<h5>Message</h5>' +
                                '<div class="btn-group btn-group-sm">' +
                                    '<button type="button" class="btn btn-default commit-message-amend" data-toggle="button">Amend</button>' +
                                    '<button type="button" class="btn btn-default commit-message-commit">Commit</button>' +
                                '</div>' +
                            '</div>' +
                            '<textarea></textarea>' +
                        '</div>')[0];
    var textArea = jQuery("textarea", self.element)[0];
    var amend = jQuery(".commit-message-amend", self.element);
    amend.click(self.onAmend);
    jQuery(".commit-message-commit", self.element).click(self.onCommit);
};

/*
 *  == Initialization =========================================================
 */
function MainUi() {
    var self = this;

    self.switchTo = function(element) {
        webui.detachChildren(self.mainView);
        self.mainView.appendChild(element);
    }

    var body = jQuery("body")[0];
    jQuery('<div id="message-box">').appendTo(body);
    var globalContainer = jQuery('<div id="global-container">').appendTo(body)[0];

    self.sideBarView = new webui.SideBarView(self);
    globalContainer.appendChild(self.sideBarView.element);

    self.mainView = jQuery('<div id="main-view">')[0];
    globalContainer.appendChild(self.mainView);

    self.historyView = new webui.HistoryView(self);
    self.workspaceView = new webui.WorkspaceView(self);
    self.filesView = new webui.FilesView(self);

    jQuery("#sidebar-files h4").click();
}

