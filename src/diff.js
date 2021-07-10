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

export function DiffView(id, sideBySide, hunkSelectionAllowed, parent) {
    let self = this;

    self.update = function(cmd, diffOpts, file, mode) {
        gitApplyType = mode;
        jQuery(".diff-stage", self.element).attr("style", "display:none");
        jQuery(".diff-cancel", self.element).attr("style", "display:none");
        jQuery(".diff-unstage", self.element).attr("style", "display:none");
        if (cmd) {
            self.gitCmd = cmd;
            self.gitDiffOpts = diffOpts;
            if (file != self.gitFile) {
                self.left.scrollTop = 0;
                self.left.scrollLeft = 0;
                self.right.scrollTop = 0;
                self.right.scrollLeft = 0;
                self.left.webuiPrevScrollTop = 0;
                self.left.webuiPrevScrollLeft = 0;
                self.right.webuiPrevScrollTop = 0;
                self.right.webuiPrevScrollLeft = 0;
            }
            self.gitFile = file;
        }
        if (self.gitCmd) {
            let fullCmd = self.gitCmd;
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
            git(fullCmd, function(diff) {
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
            let diffLines = diff.split("\n");
            self.updateSplitView(self.leftLines, diffLines, '-');
            self.updateSplitView(self.rightLines, diffLines, '+');
        } else {
            self.updateSimpleView(self.singleLines, diff);
        }
    }

    self.updateSimpleView = function(view, diff) {
        jQuery(view).empty();

        let context = { inHeader: true };
        let diffLines = diff.split("\n");
        for (let i = 0; i < diffLines.length; ++i) {
            let line = diffLines[i];
            context = self.addDiffLine(view, line, context);
        }
    }

    self.updateSplitView = function(view, diffLines, operation) {
        jQuery(view).empty();

        let context = { inHeader: true,
                        addedLines: [],
                        removedLines: [],
                      };
        for (let i = 0; i < diffLines.length; ++i) {
            let line = diffLines[i];
            let c = line[0];
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
        let lines;
        let offset;
        if (operation == '+') {
            lines = context.addedLines;
            offset = context.removedLines.length - context.addedLines.length;
        } else {
            lines = context.removedLines;
            offset = context.addedLines.length - context.removedLines.length;
        }
        lines.forEach(function(line) {
            context = self.addDiffLine(view, line, context);
        });
        if (offset > 0) {
            for (let i = 0; i < offset; ++i) {
                let pre = jQuery('<pre class="diff-view-line diff-line-phantom">').appendTo(view)[0];
                pre.appendChild(document.createTextNode(" "));
            }
        }
        return context;
    }

    self.addDiffLine = function(view, line, context) {
        let c = line[0];
        let pre = jQuery('<pre class="diff-view-line">').appendTo(view)[0];
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
        let patch = "";
        // First create the header
        for (let l = 0; l < self.leftLines.childElementCount; ++l) {
            let line = self.leftLines.children[l].textContent;
            if (line[0] == "@") {
                break;
            } else {
                patch += line + "\n";
            }
        }
        patch += self.rightLines.children[l - 1].textContent + "\n";
        // Then build the patch itself
        let refLineNo = 0;
        let patchOffset = 0;
        let hunkAddedLines = [];
        let hunkRemovedLines = [];
        for (; l < self.leftLines.childElementCount; ++l) {
            let leftElt = self.leftLines.children[l];
            let leftLine = leftElt.textContent;
            let leftCmd = leftLine[0];

            if (leftCmd == "@" || (leftCmd == " " && !jQuery(leftElt).hasClass("diff-line-phantom"))) {
                if (hunkAddedLines.length != 0 || hunkRemovedLines.length != 0) {
                    patch += self.flushSelectionPatch(hunkAddedLines, hunkRemovedLines, refLineNo, patchOffset);
                    refLineNo += hunkRemovedLines.length
                    patchOffset += hunkAddedLines.length - hunkRemovedLines.length;
                    let hunkAddedLines = [];
                    let hunkRemovedLines = [];
                }
                if (leftCmd == "@") {
                    let splittedContext = leftLine.split(" ");
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
                let rightElt = self.rightLines.children[l];
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
        let patch = "@@ -" + refLineNo + "," + hunkRemovedLines.length +" +" + (refLineNo + patchOffset) + "," + hunkAddedLines.length + " @@\n";
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
        let current;
        let other;
        if (event.target == left) {
            current = self.left;
            other = self.right;
        } else {
            current = self.right;
            other = self.left;
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
        let lineElt = event.target;
        while (lineElt && !jQuery(lineElt).hasClass("diff-view-line")) {
            lineElt = lineElt.parentElement;
        }
        if (!lineElt) {
            return;
        }
        let diffLine = lineElt.textContent;
        let cmd = diffLine[0];
        if (cmd == "+" || cmd == "-") {
            jQuery(lineElt).toggleClass("active");
        } else if (cmd == "@") {
            lineElt.webuiActive = !lineElt.webuiActive;
            for (let elt = lineElt.nextElementSibling; elt; elt = elt.nextElementSibling) {
                cmd = elt.textContent[0];
                if (cmd == "+" || cmd == "-") {
                    jQuery(elt).toggleClass("active", lineElt.webuiActive);
                } else if (cmd == "@") {
                    break;
                }
            }
        }

        let isActive = false
        let lineContainers = [self.leftLines, self.rightLines];
        for (let i = 0; i < lineContainers.length; ++i) {
            let lineContainer = lineContainers[i];
            for (let j = 0; j < lineContainer.childElementCount; ++j) {
                let elt = lineContainer.children[j];
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
        let patch = self.createSelectionPatch(reverse);
        let cmd = [ "apply", "--unidiff-zero" ];
        if (cached) {
            cmd.push("--cached");
        }
        git(cmd, patch, function (data) {
            parent.update();
        });
    }

    self.element = jQuery(id)[0];
    let panelBody = jQuery(".panel-body", self.element)[0];
    if (sideBySide) {
        self.left = jQuery('<div class="diff-view"><div class="diff-view-lines"></div></div>')[0];
        panelBody.appendChild(self.left);
        self.leftLines = self.left.firstChild;
        jQuery(self.left).scroll(self.diffViewScrolled);
        self.left.webuiPrevScrollTop = self.left.scrollTop;
        self.left.webuiPrevScrollLeft = self.left.scrollLeft;
        self.right = jQuery('<div class="diff-view"><div class="diff-view-lines"></div></div>')[0];
        panelBody.appendChild(self.right);
        self.rightLines = self.right.firstChild;
        jQuery(self.right).scroll(self.diffViewScrolled);
        self.right.webuiPrevScrollTop = self.right.scrollTop;
        self.right.webuiPrevScrollLeft = self.right.scrollLeft;
        if (hunkSelectionAllowed) {
            jQuery(self.left).click(self.handleClick);
            jQuery(self.right).click(self.handleClick);
        }
    } else {
        let single = jQuery('<div class="diff-view"><div class="diff-view-lines"></div></div>')[0];
        panelBody.appendChild(single);
        self.singleLines = single.firstChild;
    }

    jQuery(".diff-context-remove", self.element).click(self.removeContext);
    jQuery(".diff-context-add", self.element).click(self.addContext);
    jQuery(".diff-context-all", self.element).click(self.allContext);
    jQuery(".diff-ignore-whitespace", self.element).click(self.toggleIgnoreWhitespace);

    jQuery(".diff-stage", self.element).click(function() { self.applySelection(false, true); });
    jQuery(".diff-cancel", self.element).click(function() { self.applySelection(true, false); });
    jQuery(".diff-unstage", self.element).click(function() { self.applySelection(true, true); });

    self.context = 3;
    self.complete = false;
    self.ignoreWhitespace = false;
    let gitApplyType = "stage";
};

