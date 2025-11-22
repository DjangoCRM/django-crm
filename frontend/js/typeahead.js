// Generic Typeahead modal with debounce and remote fetcher
(function(){
  function debounce(fn, wait){ let t; return function(...args){ clearTimeout(t); t=setTimeout(()=>fn.apply(this,args), wait); }; }

  function open({ title='Select', placeholder='Type to search...', multiple=false, fetcher, onApply, labelKey='name', idKey='id' }){
    const wrap = document.createElement('div');
    wrap.innerHTML = `
    <div class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black bg-opacity-40" onclick="this.parentElement.remove()"></div>
      <div class="relative bg-white rounded-lg shadow-lg w-full max-w-md p-5">
        <h3 class="text-lg font-semibold mb-3">${title}</h3>
        <input id="ta-input" type="text" placeholder="${placeholder}" class="w-full border rounded px-3 py-2 mb-2"/>
        <div id="ta-list" class="border rounded max-h-72 overflow-auto"></div>
        <div class="flex justify-end space-x-2 mt-3">
          <button class="px-3 py-1 bg-gray-200 rounded" id="ta-cancel">Cancel</button>
          <button class="px-3 py-1 bg-primary-600 text-white rounded" id="ta-apply">Apply</button>
        </div>
      </div>
    </div>`;
    const modal = wrap.firstElementChild;
    document.body.appendChild(modal);
    const input = modal.querySelector('#ta-input');
    const list = modal.querySelector('#ta-list');
    const selected = new Set();

    function render(items){
      list.innerHTML = items.map(item => {
        const id = item[idKey];
        const label = item[labelKey] || String(id);
        const ctrl = multiple
          ? `<input type="checkbox" data-id="${id}" class="rounded"/>`
          : `<input type="radio" name="ta-opt" data-id="${id}" class="rounded"/>`;
        return `<label class="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 dark:hover:bg-slate-700 cursor-pointer">
          ${ctrl}
          <span class="truncate">${label}</span>
        </label>`;
      }).join('');
    }

    const doFetch = debounce(async (q)=>{
      try{
        const items = await fetcher(q||'');
        render(items || []);
      }catch(e){ list.innerHTML = `<div class='p-3 text-sm text-rose-600'>Failed to load</div>`; }
    }, 250);

    list.addEventListener('change', (e)=>{
      const id = Number(e.target.getAttribute('data-id'));
      if(!id) return;
      if(multiple){ e.target.checked ? selected.add(id) : selected.delete(id); }
      else { selected.clear(); selected.add(id); }
    });

    modal.querySelector('#ta-apply').addEventListener('click', async ()=>{
      try{
        await onApply(Array.from(selected));
      } finally { modal.remove(); }
    });
    modal.querySelector('#ta-cancel').addEventListener('click', ()=> modal.remove());

    input.addEventListener('input', (e)=> doFetch(e.target.value));
    doFetch('');
    return modal;
  }

  window.Typeahead = { open };
})();
