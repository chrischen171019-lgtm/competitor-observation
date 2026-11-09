(() => {
  if (!['http:', 'https:'].includes(location.protocol)) return;
  const host = document.getElementById('site-updates');
  if (!host) return;
  const status = document.createElement('p');
  status.className = 'note'; status.setAttribute('role', 'status');
  host.prepend(status);
  const loadedAt = host.querySelector('header p')?.textContent || '';
  async function check() {
    try {
      const response = await fetch('/api/status', {cache:'no-store'});
      if (!response.ok) throw new Error('unavailable');
      const data = await response.json();
      status.replaceChildren(document.createTextNode('本地 API 已连接 · 最近采集：' + data.generated_at + ' '));
      if (!loadedAt.includes(data.generated_at)) {
        const button = document.createElement('button'); button.className='zoom-shot';button.textContent='有新数据，刷新查看';
        button.addEventListener('click', () => location.reload());status.append(button);
      }
    } catch (_) { status.textContent='本地 API 暂不可用；当前显示已保存的采集快照。'; }
  }
  check();setInterval(check, 60000);
})();
