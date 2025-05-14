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

export async function loadGitHistory(target) {
    // Load git history
    const maxCount = 1000;
    const data = await git_async([ "log", "--date-order", "--pretty=raw", "--decorate=full", "--max-count=" + maxCount, target.name, "--" ]);
    let entries = [];
    // Parse git log output
    if (data) {
        let start = 0;
        let end = 0;
        while (end != -1) {
            end = data.indexOf("\ncommit ", start);
            let len = (end != -1) ? end - start : undefined;
            entries.push(new Entry(data.substr(start, len)));
            start = end + 1;
        }
    }
    return entries;
}

export async function updateGraph(svg, entries) {
    // Draw the graph
    const xOffset = 12;
    const lineHeight = 55;
    let streams = [];
    let streamColor = 0;
    let maxStreams = 0;
    let currentY = 0.5 * lineHeight;

    svg.innerHTML = "";  // Clear the SVG
    entries.forEach((entry) => {
        let index = 0;

        // Find streams to join
        let childCount = 0;
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
                    stream.path.setAttribute("d", stream.path.cmds + (currentY - lineHeight / 2) + " L " + x + " " + currentY);
                    streams.splice(j, 1);
                    ++removedStreams;
                }
                ++childCount;
            } else {
                if (removedStreams != 0) {
                    let x = (j + 1) * xOffset;
                    stream.path.setAttribute("d", stream.path.cmds + (currentY - lineHeight / 2) + " L " + x + " " + currentY);
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
                streamColor++;
                if (streamColor == COLORS.length) {
                    streamColor = 0;
                }
                svgPath.setAttribute("style", "stroke:" + COLORS[streamColor]);
                let origX = (index + 1) * xOffset;
                svgPath.cmds = "M " + origX + " " + currentY + " L " + x + " " + (currentY + lineHeight / 2) + " L " + x + " ";
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
            stream.path.cmds += (currentY - lineHeight / 2) + " L " + x + " " + currentY + " L " + x + " ";
        }

        let svgCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        svgCircle.setAttribute("cx", (index + 1) * xOffset);
        svgCircle.setAttribute("cy", currentY);
        svgCircle.setAttribute("r", 4);
        svg.appendChild(svgCircle);

        if (streams.length > maxStreams) {
            maxStreams = streams.length;
        }

        currentY += lineHeight;
    });
    // Set the width/height of the graph
    svg.setAttribute("height", entries.length * lineHeight);
    svg.setAttribute("width", xOffset * (maxStreams + 1));
}

export class Entry {
    // Git log entry
    parents = [];
    message = "";
    abbrevMessage = "";
    commit;
    abbrevCommitHash;
    refs = [];
    tree;
    author;
    committer;

    constructor(data) {
        const self = this;

        data.split("\n").forEach(function(line) {
            if (line.indexOf("commit ") == 0) {
                self.commit = line.substr(7, 40);
                self.abbrevCommitHash = self.commit.substr(0, 7);
                if (line.length > 47) {
                    let s = line.lastIndexOf("(") + 1;
                    let e = line.lastIndexOf(")");
                    self.refs = line.substr(s, e - s).split(", ").map((x) => new Ref(x));
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
        const end = self.message.indexOf("\n");
        if (end == -1) {
            self.abbrevMessage = self.message
        } else {
            self.abbrevMessage = self.message.substr(0, end);
        }
    }

}

export class Ref {
    // Git ref
    reftype;
    ref;

    constructor(ref) {
        const self = this;
        if (ref.indexOf("refs/remotes") == 0) {
            self.ref = ref.substr(13);
            self.reftype = "danger";
        } else if (ref.indexOf("refs/heads") == 0) {
            self.ref = ref.substr(11);
            self.reftype = "success";
        } else if (ref.indexOf("tag: refs/tags") == 0) {
            self.ref = ref.substr(15);
            self.reftype = "info";
        } else {
            self.ref = ref;
            self.reftype = "warning";
        }
    }
}

export class Person {
    // Author or committer
    name;
    email;
    date;
    formattedDate;

    constructor(data) {
        const self = this;
        const nameEnd = data.indexOf("<");
        this.name = data.substr(0, nameEnd - 1);
        const emailEnd = data.indexOf(">", nameEnd);
        this.email = data.substr(nameEnd + 1, emailEnd - nameEnd - 1);
        const dateEnd = data.indexOf(" ", emailEnd + 2);
        const secs = data.substr(emailEnd + 2, dateEnd - emailEnd - 2);
        this.date = new Date(0);
        this.date.setUTCSeconds(parseInt(secs));
        this.formattedDate = this.date.toISOString().substring(0, 16).replace('T', ' ');
    }

}
