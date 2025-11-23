import { Component } from '@angular/core';
import { SidebarService } from '../../services/sidebar.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-backdrop',
  imports: [
    CommonModule,
  ],
  templateUrl: './backdrop.component.html',
})

export class BackdropComponent {
  readonly isMobileOpen$;

  constructor(private sidebarService: SidebarService) {
    this.isMobileOpen$ = this.sidebarService.isMobileOpen$;
  }

  closeSidebar() {
    this.sidebarService.setMobileOpen(false);
  }
}
