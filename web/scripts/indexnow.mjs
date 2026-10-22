// Tell Bing, Yandex, Seznam and other IndexNow engines that pages changed (Bing also feeds several AI search products).
// Run after a deploy, once https://vocalface.com/3107ea5174655a05ff476d4710f37c77.txt is live:   node scripts/indexnow.mjs [https://vocalface.com]
// It reads the live sitemap and submits every URL. Google does not use IndexNow: use Search Console for Google.
const KEY = "3107ea5174655a05ff476d4710f37c77";
const site = (process.argv[2] || "https://vocalface.com").replace(/\/+$/, "");
const host = new URL(site).host;
const keyCheck = await fetch(`${site}/${KEY}.txt`);
if (!keyCheck.ok || (await keyCheck.text()).trim() !== KEY) {
  console.error(`The key file ${site}/${KEY}.txt is not live yet: deploy first.`);
  process.exit(1);
}
const xml = await (await fetch(`${site}/sitemap.xml`)).text();
const urlList = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]).filter((u) => new URL(u).host === host);
if (!urlList.length) { console.error("No same-host URLs in the sitemap (is the site still advertising localhost?)"); process.exit(1); }
const r = await fetch("https://api.indexnow.org/indexnow", {
  method: "POST", headers: { "content-type": "application/json; charset=utf-8" },
  body: JSON.stringify({ host, key: KEY, keyLocation: `${site}/${KEY}.txt`, urlList }),
});
console.log(`IndexNow: HTTP ${r.status} for ${urlList.length} URLs`);
