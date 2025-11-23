(function(){
  const STORAGE_KEY = 'theme';
  const root = document.documentElement;
  function applyTheme(theme){
    if(theme === 'dark') root.classList.add('dark');
    else root.classList.remove('dark');
    // Update icon
    const icon = document.getElementById('theme-toggle-icon');
    if(icon){
      if(root.classList.contains('dark')){
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
      } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
      }
    }
  }
  function getPreferred(){
    const stored = localStorage.getItem(STORAGE_KEY);
    if(stored === 'dark' || stored === 'light') return stored;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  // Initial
  applyTheme(getPreferred());
  // Toggle handler after DOM ready
  document.addEventListener('DOMContentLoaded', function(){
    const btn = document.getElementById('theme-toggle');
    if(!btn) return;
    btn.addEventListener('click', function(){
      const next = root.classList.contains('dark') ? 'light' : 'dark';
      localStorage.setItem(STORAGE_KEY, next);
      applyTheme(next);
    });
    // Ensure icon matches state
    applyTheme(root.classList.contains('dark') ? 'dark' : 'light');
  });
})();
