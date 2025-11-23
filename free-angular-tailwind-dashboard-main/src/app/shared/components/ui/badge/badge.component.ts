import { CommonModule } from '@angular/common';
import { Component, HostBinding, Input } from '@angular/core';
import { SafeHtmlPipe } from '../../../pipe/safe-html.pipe';

type BadgeVariant = 'light' | 'solid';
type BadgeSize = 'sm' | 'md';
type BadgeColor = 'primary' | 'success' | 'error' | 'warning' | 'info' | 'light' | 'dark';

@Component({
  selector: 'app-badge',
  imports: [CommonModule,SafeHtmlPipe],
  templateUrl: './badge.component.html',
})
export class BadgeComponent {
  @Input() variant: BadgeVariant = 'light';
  @Input() size: BadgeSize = 'md';
  @Input() color: BadgeColor = 'primary';
  @Input() startIcon?: string; // SVG or HTML string
  @Input() endIcon?: string;   // SVG or HTML string

  @HostBinding('class') get hostClasses(): string {
    // return `${this.baseStyles} ${this.sizeClass} ${this.colorStyles}`;
    return `flex`;
  }

  get baseStyles() {
    return 'inline-flex items-center px-2.5 py-0.5 justify-center gap-1 rounded-full font-medium';
  }

  get sizeClass() {
    return {
      sm: 'text-theme-xs',
      md: 'text-sm',
    }[this.size];
  }

  get colorStyles() {
    const variants = {
      light: {
        primary: 'bg-brand-50 text-brand-500 dark:bg-brand-500/15 dark:text-brand-400',
        success: 'bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-500',
        error: 'bg-error-50 text-error-600 dark:bg-error-500/15 dark:text-error-500',
        warning: 'bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-orange-400',
        info: 'bg-blue-light-50 text-blue-light-500 dark:bg-blue-light-500/15 dark:text-blue-light-500',
        light: 'bg-gray-100 text-gray-700 dark:bg-white/5 dark:text-white/80',
        dark: 'bg-gray-500 text-white dark:bg-white/5 dark:text-white',
      },
      solid: {
        primary: 'bg-brand-500 text-white dark:text-white',
        success: 'bg-success-500 text-white dark:text-white',
        error: 'bg-error-500 text-white dark:text-white',
        warning: 'bg-warning-500 text-white dark:text-white',
        info: 'bg-blue-light-500 text-white dark:text-white',
        light: 'bg-gray-400 dark:bg-white/5 text-white dark:text-white/80',
        dark: 'bg-gray-700 text-white dark:text-white',
      },
    };
    return variants[this.variant][this.color];
  }
}