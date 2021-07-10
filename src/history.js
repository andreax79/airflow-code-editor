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

import { LogView } from "./log";
import { DiffView } from "./diff";

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

export function TabBox(buttons) {
    let self = this;

    self.itemClicked = function(event) {
        self.updateSelection(event.target.parentElement);
        return false;
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

    for (let i = 0; i < buttons.length; ++i) {
        let item = buttons[i];
        let li = jQuery('<li><a href="#">' + item[0] + '</a></li>');
        li.appendTo(self.element);
        li.click(self.itemClicked);
        li[0].callback = item[1];
    }
};

/*
 * == CommitView ==============================================================
 */
export function CommitView(id, stack) {
    let self = this;

    self.update = function(entry) {
        if (currentCommit == entry.commit) {
            // We already display the right data. No need to update.
            return;
        }
        currentCommit = entry.commit;
        self.showDiff();
        buttonBox.select(0);
        diffView.update([ "show" ], [entry.commit]);
        // Update tree
        self.stack.updateStack(entry.tree)
    };

    self.showDiff = function() {
        jQuery(id).find('.tree-view').hide();
        jQuery(id).find('.diff-view-container').show();
    };

    self.showTree = function() {
        jQuery(id).find('.diff-view-container').hide();
        jQuery(id).find('.tree-view').show();
    };

    self.stack = stack;
    let currentCommit = null;
    self.element = jQuery(id)[0];
    let commitViewHeader = jQuery(id).find('.commit-view-header')[0];
    let buttonBox = new TabBox([["Commit", self.showDiff], ["Tree", self.showTree]]);
    commitViewHeader.appendChild(buttonBox.element);
    let diffView = new DiffView(id + ' .diff-view-container', false, false, self);
};

/*
 * == HistoryView =============================================================
 */
export function HistoryView(stack) {
    let self = this;

    self.update = function(item) {
        self.logView.update(item.name);
        document.location.hash = item.id + '/' + item.name;
        self.stack.updateStack(item.name)
    };

    self.stack = stack;
    self.element = jQuery('#history-view')[0];
    self.logView = new LogView('#log-view', self);
    self.commitView = new CommitView('#commit-view', stack);
};

