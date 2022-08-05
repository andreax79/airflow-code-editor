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

import { DiffView } from "./diff";
import { CommitMessageView } from "./commit";
import { ChangedFilesView } from "./changed_files";

export class WorkspaceView {

    constructor() {
        const self = this;
        self.element = jQuery('#workspace-view')[0];
        self.diffView = new DiffView('#workspace-diff-view .diff-view-container', self);
        self.workspaceEditor = jQuery("#workspace-editor", self.element)[0];
        self.workingCopyView = new ChangedFilesView(self, "working-copy", "Working Copy");
        self.workspaceEditor.appendChild(self.workingCopyView.element);
        self.commitMessageView = new CommitMessageView(self);
        self.workspaceEditor.appendChild(self.commitMessageView.element);
        self.stagingAreaView = new ChangedFilesView(self, "staging-area", "Staging Area");
        self.workspaceEditor.appendChild(self.stagingAreaView.element);
    }

    update() {
        const self = this;
        document.location.hash = 'workspace';
        self.workingCopyView.update();
        self.stagingAreaView.update();
        self.commitMessageView.update();
        if (self.workingCopyView.getSelectedItemsCount() + self.stagingAreaView.getSelectedItemsCount() == 0) {
            self.diffView.update(undefined, undefined, undefined);
        }
    }

}
