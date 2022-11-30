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

import { COLORS, git_async } from "./commons";

export function LogView(id, historyView) {
    const self = this;

    self.update = async function(ref) {
        jQuery(svg).empty();
        streams = []
        jQuery(content).empty();
        self.nextRef = ref;
        self.populate();
    };

    self.populate = async function() {
        currentSelection = null;
        const maxCount = 1000;
        if (content.childElementCount > 0) {
            // The last node is the 'Show more commits placeholder'. Remove it.
            content.removeChild(content.lastElementChild);
        }
        const startAt = content.childElementCount;
        const data = await git_async([ "log", "--date-order", "--pretty=raw", "--decorate=full", "--max-count=" + String(maxCount + 1), String(self.nextRef), "--" ]);
        if (data) {
            let start = 0;
            let count = 0;
            self.nextRef = undefined;
            while (true) {
                let end = data.indexOf("\ncommit ", start);
                let len = (end != -1) ? end - start : undefined;
                let entry = new Entry(self, data.substr(start, len));
                if (count < maxCount) {
                    content.appendChild(entry.element);
                    if (!self.lineHeight) {
                        self.lineHeight = Math.ceil(jQuery(entry.element).outerHeight() / 2) * 2;
                    }
                    entry.element.setAttribute("style", "height:" + self.lineHeight + "px");
                    if (!currentSelection) {
                        currentSelection = entry;
                        jQuery(entry.element).addClass("active");
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
                let moreTag = jQuery('<a class="log-entry log-entry-more list-group-item">');
                jQuery('<a class="list-group-item-text">Show previous commits</a>').appendTo(moreTag[0]);
                moreTag.click(self.populate);
                moreTag.appendTo(content);
            }

            self.updateGraph(startAt);
        };
    };

    self.updateGraph = function(startAt) {
        // Draw the graph
        let currentY = (startAt + 0.5) * self.lineHeight;
        let maxLeft = 0;
        if (startAt == 0) {
            streamColor = 0;
        }
        let xOffset = null;
        for (let i = startAt; i < content.children.length; ++i) {
            let entry = content.children[i].model;
            if (!entry) {
                break;
            }
            let index = 0;
            entry.element.webuiLeft = streams.length;

            // Find streams to join
            let childCount = 0;
            xOffset = 12;
            let removedStreams = 0;
            for (let j = 0; j < streams.length;) {
                let stream = streams[j];
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
                        let x = (index + 1) * xOffset;
                        stream.path.setAttribute("d", stream.path.cmds + (currentY - self.lineHeight / 2) + " L " + x + " " + currentY);
                        streams.splice(j, 1);
                        ++removedStreams;
                    }
                    ++childCount;
                } else {
                    if (removedStreams != 0) {
                        let x = (j + 1) * xOffset;
                        stream.path.setAttribute("d", stream.path.cmds + (currentY - self.lineHeight / 2) + " L " + x + " " + currentY);
                    }
                    ++j;
                }
            }

            // Add new streams
            for (let j = 0; j < entry.parents.length; ++j) {
                let parent = entry.parents[j];
                let x = (index + j + 1) * xOffset;
                if (j != 0 || streams.length == 0) {
                    let svgPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
                    ++streamColor
                    if (streamColor == COLORS.length) {
                        streamColor = 0;
                    }
                    svgPath.setAttribute("style", "stroke:" + COLORS[streamColor]);
                    let origX = (index + 1) * xOffset;
                    svgPath.cmds = "M " + origX + " " + currentY + " L " + x + " " + (currentY + self.lineHeight / 2) + " L " + x + " ";
                    svg.appendChild(svgPath);
                    let obj = {
                        sha1: parent,
                        path: svgPath,
                    };
                    streams.splice(index + j, 0, obj);
                }
            }
            for (let j = index + entry.parents.length; j < streams.length; ++j) {
                let stream = streams[j];
                let x = (j + 1) * xOffset;
                stream.path.cmds += (currentY - self.lineHeight / 2) + " L " + x + " " + currentY + " L " + x + " ";
            }

            let svgCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
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
        for (let i = startAt; i < content.children.length; ++i) {
            let element = content.children[i];
            if (element.model) {
                let minLeft = Math.min(maxLeft, 3);
                let left = element ? Math.max(minLeft, element.webuiLeft) : minLeft;
                element.setAttribute("style", element.getAttribute("style") + ";padding-left:" + (left + 1) * xOffset + "px");
            }
        }
        for (let i = 0; i < streams.length; ++i) {
            let stream = streams[i];
            stream.path.setAttribute("d", stream.path.cmds + currentY);
        }
    }

    function Person(data) {
        let nameEnd = data.indexOf("<");
        this.name = data.substr(0, nameEnd - 1);
        let emailEnd = data.indexOf(">", nameEnd);
        this.email = data.substr(nameEnd + 1, emailEnd - nameEnd - 1);
        let dateEnd = data.indexOf(" ", emailEnd + 2);
        let secs = data.substr(emailEnd + 2, dateEnd - emailEnd - 2);
        this.date = new Date(0);
        this.date.setUTCSeconds(parseInt(secs));
        this.formattedDate = this.date.toISOString().substring(0, 16).replace('T', ' ');
    };

    function Entry(logView, data) {
        let self = this;

        self.abbrevCommitHash = function() {
            return self.commit.substr(0, 7);
        };

        self.abbrevMessage = function() {
            let end = self.message.indexOf("\n");
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
                                    '<span class="log-entry-date">' + self.author.formattedDate + '&nbsp;</span> ' +
                                    '<span class="badge">' + self.abbrevCommitHash() + '</span>' +
                                '</header>' +
                                '<p class="list-group-item-text"></p>' +
                             '</a>')[0];
            // jQuery('<span>' + self.author.name + ' &lt;' + self.author.email + '&gt;</span>').appendTo(jQuery("h6", self.element));
            jQuery('<span>' + self.author.name + '</span>').appendTo(jQuery("h6", self.element));
            jQuery(".list-group-item-text", self.element)[0].appendChild(document.createTextNode(self.abbrevMessage()));
            if (self.refs) {
                let entryName = jQuery("h6", self.element);
                self.refs.forEach(function (ref) {
                    let reftype = null;
                    if (ref.indexOf("refs/remotes") == 0) {
                        ref = ref.substr(13);
                        reftype = "danger";
                    } else if (ref.indexOf("refs/heads") == 0) {
                        ref = ref.substr(11);
                        reftype = "success";
                    } else if (ref.indexOf("tag: refs/tags") == 0) {
                        ref = ref.substr(15);
                        reftype = "info";
                    } else {
                        reftype = "warning";
                    }
                    jQuery('<span>&nbsp;</span><span class="label label-' + reftype + '">' + ref + '</span>').insertAfter(entryName);
                });
            }
            self.element.model = self;
            let model = self;
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
                historyView.updateCommit(self);
            }
        };

        self.parents = [];
        self.message = ""

        data.split("\n").forEach(function(line) {
            if (line.indexOf("commit ") == 0) {
                self.commit = line.substr(7, 40);
                if (line.length > 47) {
                    self.refs = []
                    let s = line.lastIndexOf("(") + 1;
                    let e = line.lastIndexOf(")");
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

    self.element = jQuery(id)[0];
    let svg = self.element.children[0];
    let content = self.element.children[1];
    let currentSelection = null;
    let lineHeight = null;
    let streams = [];
    let streamColor = 0;
};
