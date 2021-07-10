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

export function CommitMessageView(workspaceView) {
    let self = this;

    self.onAmend = function() {
        if (!amend.hasClass("active") && textArea.value.length == 0) {
            git([ "log", "--pretty=format:%B", "-n", "1" ], function(data) {
                textArea.value = data;
            });
        }
    };

    self.onCommit = function() {
        if (workspaceView.stagingAreaView.filesCount == 0 && !amend.hasClass("active")) {
            showError("No files staged for commit");
        } else if (textArea.value.length == 0) {
            showError("Enter a commit message first");
        } else {
            let cmd = [ "commit" ];
            if (amend.hasClass("active")) {
                cmd.push("--amend");
            }
            cmd.push("-m");
            cmd.push(textArea.value)
            git(cmd, function(data) {
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
    let textArea = jQuery("textarea", self.element)[0];
    let amend = jQuery(".commit-message-amend", self.element);
    amend.click(self.onAmend);
    jQuery(".commit-message-commit", self.element).click(self.onCommit);
};
