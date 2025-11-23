import { Component } from '@angular/core';
import { AvatarComponent } from '../../../shared/components/ui/avatar/avatar.component';
import { ComponentCardComponent } from '../../../shared/components/common/component-card/component-card.component';
import { PageBreadcrumbComponent } from '../../../shared/components/common/page-breadcrumb/page-breadcrumb.component';

@Component({
  selector: 'app-avatar-element',
  imports: [
    AvatarComponent,
    ComponentCardComponent,
    PageBreadcrumbComponent
  ],
  templateUrl: './avatar-element.component.html',
  styles: ``
})
export class AvatarElementComponent {

}
