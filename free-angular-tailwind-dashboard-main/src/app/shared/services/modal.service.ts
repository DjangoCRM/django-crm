import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ModalService {
  private isOpenSubject = new BehaviorSubject<boolean>(false);

  /** Observable for modal open state */
  isOpen$: Observable<boolean> = this.isOpenSubject.asObservable();

  /** Get current value synchronously */
  get isOpen(): boolean {
    return this.isOpenSubject.value;
  }

  /** Open the modal */
  openModal(): void {
    this.isOpenSubject.next(true);
  }

  /** Close the modal */
  closeModal(): void {
    this.isOpenSubject.next(false);
  }

  /** Toggle the modal */
  toggleModal(): void {
    this.isOpenSubject.next(!this.isOpenSubject.value);
  }
}