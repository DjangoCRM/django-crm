import { Component } from '@angular/core';
import { ThemeService } from '../../../services/theme.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-theme-toggle-two',
  imports: [
    CommonModule,
  ],
  templateUrl: './theme-toggle-two.component.html',
  styles: ``
})
export class ThemeToggleTwoComponent {

  theme$;

  constructor(private themeService: ThemeService) {
    this.theme$ = this.themeService.theme$;
  }

  toggleTheme() {
    this.themeService.toggleTheme();
  }
}
