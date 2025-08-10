// inject-backlink.js
const fs = require('fs');
const path = require('path');

const MARK = '<!-- BACK2DASHBOARD-INJECTED -->';
const INJECT = `
${MARK}
<script>
  (function () {
    function getBasePath() {
      const parts = location.pathname.split('/').filter(Boolean);
      // Proje sayfası ise "/repo-adi/", user/org pages ise "/"
      return parts.length > 0 ? \`/\${parts[0]}/\` : '/';
    }
    const base = getBasePath();
    document.querySelectorAll('a.back-to-dashboard').forEach(a => {
      a.setAttribute('href', \`\${base}index.html\`);
      a.addEventListener('click', function (e) {
        e.preventDefault();
        window.location.href = \`\${base}index.html\`;
      });
    });
  })();
</script>
`;

function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const stat = fs.statSync(p);
    if (stat.isDirectory()) {
      // .git ve node_modules’i atla
      if (name === '.git' || name === 'node_modules') continue;
      walk(p);
    } else if (stat.isFile() && /\.html?$/i.test(name)) {
      inject(p);
    }
  }
}

function inject(file) {
  let html = fs.readFileSync(file, 'utf8');

  // Zaten enjekte edilmişse dokunma
  if (html.includes(MARK)) return;

  // Linki standardize et (varsa)
  html = html.replace(
    /<a([^>]*?)class="([^"]*?\bback-to-dashboard\b[^"]*?)"([^>]*)>[\s\S]*?<\/a>/i,
    '<a class="back-to-dashboard">← Back to Main Dashboard</a>'
  );

  // back-to-dashboard linki hiç yoksa dosyayı atla (isteğe bağlı)
  if (!/class="[^"]*\bback-to-dashboard\b[^"]*"/.test(html)) return;

  // </body></html> öncesine script’i ekle
  if (/<\/body>\s*<\/html>\s*$/i.test(html)) {
    html = html.replace(/<\/body>\s*<\/html>\s*$/i, `${INJECT}\n</body>\n</html>`);
  } else if (/<\/body>/i.test(html)) {
    html = html.replace(/<\/body>/i, `${INJECT}\n</body>`);
  } else {
    // Çok nadir: body yoksa en sona ekle
    html += `\n${INJECT}\n`;
  }

  fs.writeFileSync(file, html, 'utf8');
  console.log('Updated:', file);
}

walk(process.cwd());
console.log('Done.');
