// public/rebalance/rebalance.js
// ─────────────────────────────────────────────────────────────────────────────
// Fetches rebalance event data from the Cloudflare Worker JSON API and renders
// the full page: breadcrumbs, hero, inclusions/exclusions cards, constituents
// grid, prev/next navigation, and all SEO meta tags.
//
// URL pattern expected: /rebalance/<index_slug>/<YYYY-MM-DD>
// API endpoint used:    /api/rebalance/<index_slug>/<YYYY-MM-DD>
// API response shape:   { event, constituents[], inclusions[], exclusions[], prev_event, next_event }
// ─────────────────────────────────────────────────────────────────────────────

// Script is loaded at bottom of <body>, so DOM is already ready.
// Using an IIFE instead of DOMContentLoaded — the event has already fired
// by the time a bottom-of-body script runs, so addEventListener never triggers.
(async () => {
    // ── 1. Parse slug and date from the current URL ───────────────────────────
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    // pathParts = ['rebalance', index_slug, date]
    const indexSlug = pathParts[1];
    const date      = pathParts[2];

    const root = document.getElementById('rebalance-root');
    console.log(`Fetching rebalance data for index_slug="${indexSlug}", date="${date}"`);
    if (!indexSlug || !date) {
        root.innerHTML = '<div style="color:#ef4444;padding:40px;text-align:center;">Invalid URL — missing index slug or date.</div>';
        return;
    }

    // ── 2. Fetch data from the JSON API ──────────────────────────────────────
    try {
        const res = await fetch(`/api/rebalance/${indexSlug}/${date}`);
        console.log(`API response status: ${res}`);
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        const { event, constituents, inclusions, exclusions, prev_event, next_event } = await res.json();

        if (!event) throw new Error('Event not found in response');

        // ── 3. Derive display names ───────────────────────────────────────────
        // index_type from DB is e.g. "Nifty50" — add a space before the digits
        const formattedIndexName = event.index_type
            ? event.index_type.replace(/([a-zA-Z])(\d)/, '$1 $2')
            : indexSlug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

        // ── 4. Inject SEO meta tags ───────────────────────────────────────────
        applySEOTags({
            inclusions,
            exclusions,
            formattedIndexName,
            effectiveDate: event.effective_date,
            indexSlug,
            indexType: event.index_type
        });

        // ── 5. Build heading text (matches original Jinja2 logic) ─────────────
        const incLen = inclusions.length;
        const excLen = exclusions.length;

        const incTitleList = inclusions.map(toTitleCase);
        const excTitleList = exclusions.map(toTitleCase);
        const incText = incLen <= 3 ? incTitleList.join(', ') : incTitleList.slice(0, 2).join(', ') + '...';
        const excText = excLen <= 3 ? excTitleList.join(', ') : excTitleList.slice(0, 2).join(', ') + ' and others';

        let h1HTML = '';
        if (incLen && excLen) {
            h1HTML = `NSE to Add <span style="font-weight:600;color:#a5b4fc;">${escHtml(incText)}</span> and Drop <span style="font-weight:600;color:#f472b6;">${escHtml(excText)}</span> from ${escHtml(formattedIndexName)}`;
        } else if (incLen) {
            h1HTML = `NSE to Add <span style="font-weight:600;color:#a5b4fc;">${escHtml(incText)}</span> to ${escHtml(formattedIndexName)}`;
        } else if (excLen) {
            h1HTML = `NSE to Drop <span style="font-weight:600;color:#f472b6;">${escHtml(excText)}</span> from ${escHtml(formattedIndexName)}`;
        } else {
            h1HTML = `NSE ${escHtml(formattedIndexName)} Rebalancing`;
        }

        // ── 6. Build prev / next nav buttons ─────────────────────────────────
        const prevHref = prev_event
            ? `/rebalance/${prev_event.index_type.toLowerCase().replace(/\s+/g, '-')}/${prev_event.effective_date}`
            : null;
        const nextHref = next_event
            ? `/rebalance/${next_event.index_type.toLowerCase().replace(/\s+/g, '-')}/${next_event.effective_date}`
            : null;

        const prevBtn = prevHref
            ? `<a href="${prevHref}" class="nav-event-btn prev-btn">
                   <span class="nav-label">← Previous Event</span>
                   <strong class="nav-title">${escHtml(prev_event.effective_date)} (${escHtml(prev_event.index_type)})</strong>
               </a>`
            : `<div class="nav-event-btn prev-btn disabled">
                   <span class="nav-label">← Previous Event</span>
                   <strong class="nav-title">Inception Limit Reached</strong>
               </div>`;

        const nextBtn = nextHref
            ? `<a href="${nextHref}" class="nav-event-btn next-btn">
                   <span class="nav-label">Next Event →</span>
                   <strong class="nav-title">${escHtml(next_event.effective_date)} (${escHtml(next_event.index_type)})</strong>
               </a>`
            : `<div class="nav-event-btn next-btn disabled">
                   <span class="nav-label">Next Event →</span>
                   <strong class="nav-title">Latest Event Reached</strong>
               </div>`;

        // ── 7. Render full page content ───────────────────────────────────────
        root.innerHTML = `
            <!-- Breadcrumbs for SEO crawl depth -->
            <div class="breadcrumbs" aria-label="Breadcrumb">
                <a href="/">Home</a>
                <span>/</span>
                <a href="/archive">Archive</a>
                <span>/</span>
                <span aria-current="page">${escHtml(formattedIndexName)} &ndash; ${escHtml(event.effective_date)}</span>
            </div>

            <!-- Event Hero Header -->
            <header class="header-section">
                <h1 class="index-title">${h1HTML}</h1>
                <div class="event-date-badge">${escHtml(event.effective_date)}</div>
                <!-- CSV Download button -->
                <div style="margin-top:20px;">
                    <a href="/download?index_type=${encodeURIComponent(event.index_type)}&start_date=${encodeURIComponent(event.effective_date)}&end_date=${encodeURIComponent(event.effective_date)}"
                       class="btn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7 10 12 15 17 10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                        Download Constituents CSV
                    </a>
                </div>
            </header>

            <!-- Inclusions & Exclusions Split Layout -->
            <section class="changes-grid">
                <!-- Inclusions -->
                <div class="change-card inclusions-card">
                    <div class="card-header">
                        <h2 class="card-title inc">Inclusions (Added)</h2>
                        <span class="card-count inc">${incLen} Stock${incLen !== 1 ? 's' : ''}</span>
                    </div>
                    <div class="ticker-list">
                        ${incLen
                            ? inclusions.map(t => `<span class="ticker-badge inc-ticker">${escHtml(t)}</span>`).join('')
                            : '<span class="empty-change">No stock inclusions during this cycle.</span>'}
                    </div>
                </div>

                <!-- Exclusions -->
                <div class="change-card exclusions-card">
                    <div class="card-header">
                        <h2 class="card-title exc">Exclusions (Removed)</h2>
                        <span class="card-count exc">${excLen} Stock${excLen !== 1 ? 's' : ''}</span>
                    </div>
                    <div class="ticker-list">
                        ${excLen
                            ? exclusions.map(t => `<span class="ticker-badge exc-ticker">${escHtml(t)}</span>`).join('')
                            : '<span class="empty-change">No stock exclusions during this cycle.</span>'}
                    </div>
                </div>
            </section>

            <!-- Searchable Constituent Universe -->
            <section class="universe-section">
                <div class="section-header">
                    <h2 class="section-title">Complete Constituents (${constituents.length} Stocks)</h2>
                    <input type="text" id="constituentsSearch" class="universe-search"
                           placeholder="Search constituent ticker..."
                           oninput="searchConstituents()">
                </div>
                <div class="universe-grid" id="universeGrid">
                    ${constituents.map(sym => `<div class="constituent-card" data-symbol="${escHtml(sym.toLowerCase())}">${escHtml(sym)}</div>`).join('')}
                </div>
            </section>

            <!-- Dynamically populated FAQ Section -->
            <section class="faq-section">
                <h2 class="faq-title">Frequently Asked Questions</h2>
                <div class="faq-grid" id="faqGridContainer">
                    <!-- FAQ Items will be injected by JS -->
                </div>
            </section>

            <!-- Chronological Navigation (internal linking for Googlebot) -->
            <footer class="nav-events-footer">
                <nav class="nav-events" aria-label="Chronological navigation">
                    ${prevBtn}
                    ${nextBtn}
                </nav>
                <div class="back-link-container">
                    <a href="/archive" class="back-link"><span>←</span> Back to Archive Directory</a>
                </div>
            </footer>
        `;

        // Render dynamic FAQ and inject JSON-LD Schema
        generateAndRenderFAQ({
            event,
            inclusions,
            exclusions,
            formattedIndexName,
            date: event.effective_date,
            indexSlug
        });

    } catch (err) {
        root.innerHTML = `<div style="color:#ef4444;padding:40px;text-align:center;">Rebalancing event not found.<br><small>${escHtml(err.message)}</small></div>`;
    }
})();

// ── Constituent search (global so oninput can reach it) ───────────────────────
function searchConstituents() {
    const query = document.getElementById('constituentsSearch').value.toLowerCase();
    document.querySelectorAll('.constituent-card').forEach(card => {
        card.style.display = card.dataset.symbol.includes(query) ? '' : 'none';
    });
}

// ── SEO tag injection ─────────────────────────────────────────────────────────
/**
 * Injects all SEO meta tags that were previously generated by Jinja2 on the server.
 * Called once after the API response is received.
 * @param {Object} opts
 */
function applySEOTags({ inclusions, exclusions, formattedIndexName, effectiveDate, indexSlug, indexType }) {
    const incLen = inclusions.length;
    const excLen = exclusions.length;
    const incTitleList = inclusions.map(toTitleCase);
    const excTitleList = exclusions.map(toTitleCase);
    const incText = incLen <= 3 ? incTitleList.join(', ') : incTitleList.slice(0, 2).join(', ') + '...';
    const excText = excLen <= 3 ? excTitleList.join(', ') : excTitleList.slice(0, 2).join(', ') + ' and others';

    // Dynamic <title>
    let title = '';
    if (incLen && excLen) {
        title = `NSE to Add ${incText} and Drop ${excText} from ${formattedIndexName} on ${effectiveDate} - Niftyhistory.in`;
    } else if (incLen) {
        title = `NSE to Add ${incText} to ${formattedIndexName} on ${effectiveDate} - Niftyhistory.in`;
    } else if (excLen) {
        title = `NSE to Drop ${excText} from ${formattedIndexName} on ${effectiveDate} - Niftyhistory.in`;
    } else {
        title = `NSE ${formattedIndexName} Rebalancing on ${effectiveDate} - Niftyhistory.in`;
    }
    document.title = title;

    // Meta description
    const description = `View the full structural changes of the ${formattedIndexName} on ${effectiveDate}. ` +
        `Stock Inclusions: ${inclusions.join(', ') || 'None'}. ` +
        `Stock Exclusions: ${exclusions.join(', ') || 'None'}. ` +
        `Complete historical constituents list available for download.`;
    setMeta('name', 'description', description);

    // Canonical link
    const canonicalUrl = `https://niftyhistory.in/rebalance/${indexSlug}/${effectiveDate}`;
    let canonEl = document.head.querySelector("link[rel='canonical']");
    if (!canonEl) {
        canonEl = document.createElement('link');
        canonEl.rel = 'canonical';
        document.head.appendChild(canonEl);
    }
    canonEl.href = canonicalUrl;

    // Open Graph
    setMeta('property', 'og:type', 'article');
    setMeta('property', 'og:url', canonicalUrl);
    setMeta('property', 'og:title', title);
    setMeta('property', 'og:description', description);
    setMeta('property', 'og:image', 'https://niftyhistory.in/images/seo-banner.jpg');

    // Twitter Card
    setMeta('name', 'twitter:card', 'summary_large_image');
    setMeta('name', 'twitter:url', canonicalUrl);
    setMeta('name', 'twitter:title', title);
    setMeta('name', 'twitter:description', description);
    setMeta('name', 'twitter:image', 'https://niftyhistory.in/images/seo-banner.jpg');

    // JSON-LD structured data: Article + Dataset + BreadcrumbList schemas
    const jsonLd = [
        {
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: `${formattedIndexName} Rebalancing on ${effectiveDate}`,
            description: `Historical additions and removals of stocks for the ${formattedIndexName} on ${effectiveDate}`,
            datePublished: effectiveDate,
            author: { '@type': 'Organization', name: 'Niftyhistory.in' },
            publisher: { '@type': 'Organization', name: 'Niftyhistory.in' }
        },
        {
            '@context': 'https://schema.org',
            '@type': 'Dataset',
            name: `${formattedIndexName} Constituents - Rebalancing on ${effectiveDate}`,
            description: `Historical survivorship-bias-free constituent stock list for the ${formattedIndexName} following the structural rebalancing on ${effectiveDate}.`,
            license: 'https://creativecommons.org/licenses/by/4.0/',
            distribution: {
                '@type': 'DataDownload',
                encodingFormat: 'text/csv',
                contentUrl: `https://niftyhistory.in/download?index_type=${encodeURIComponent(indexType)}&start_date=${effectiveDate}&end_date=${effectiveDate}`
            }
        },
        {
            // BreadcrumbList — enables rich breadcrumb display in Google search results
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            itemListElement: [
                { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://niftyhistory.in/' },
                { '@type': 'ListItem', position: 2, name: 'Archive', item: 'https://niftyhistory.in/archive' },
                { '@type': 'ListItem', position: 3, name: `${formattedIndexName} – ${effectiveDate}`, item: canonicalUrl }
            ]
        }
    ];
    // Update the static BreadcrumbList stub (id="ld-breadcrumb") injected by index.html,
    // or fall back to creating a new script tag if not found.
    let ldScript = document.head.querySelector('#ld-breadcrumb') ||
                   document.head.querySelector('script[type="application/ld+json"]');
    if (!ldScript) {
        ldScript = document.createElement('script');
        ldScript.type = 'application/ld+json';
        document.head.appendChild(ldScript);
    }
    ldScript.text = JSON.stringify(jsonLd, null, 2);

    // Keywords meta — used by Bing; free signal with no downside
    setMeta('name', 'keywords', `${formattedIndexName}, NSE rebalancing, ${effectiveDate}, index constituents, stock inclusions, stock exclusions, historical index data, nifty history`);
    // Author
    setMeta('name', 'author', 'Niftyhistory.in');
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Creates or updates a <meta> tag in the document head.
 * @param {string} attrKey   - Attribute name: 'name' or 'property'
 * @param {string} attrValue - Attribute value: e.g. 'description' or 'og:title'
 * @param {string} content   - Content value to set
 */
function setMeta(attrKey, attrValue, content) {
    let el = document.head.querySelector(`meta[${attrKey}='${attrValue}']`);
    if (!el) {
        el = document.createElement('meta');
        el.setAttribute(attrKey, attrValue);
        document.head.appendChild(el);
    }
    el.content = content;
}

/** Title-case a ticker string (first letter upper, rest lower) */
function toTitleCase(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/** Escape HTML special characters to prevent XSS in innerHTML */
function escHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

/**
 * Generates dynamic FAQ questions, outputs them to the page, and injects FAQPage JSON-LD schema.
 */
function generateAndRenderFAQ({ event, inclusions, exclusions, formattedIndexName, date, indexSlug }) {
    const incListStr = inclusions.length > 0 ? inclusions.join(', ') : 'None';
    const excListStr = exclusions.length > 0 ? exclusions.join(', ') : 'None';

    // Format ISO date (e.g. "2026-01-12") to reader-friendly format (e.g. "12 January 2026")
    const friendlyDate = new Date(date).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });

    const faqs = [
        {
            q: `What were the rebalancing changes for ${formattedIndexName} on ${friendlyDate}?`,
            a: `On ${friendlyDate}, the ${formattedIndexName} index was rebalanced. A total of ${inclusions.length} new stock(s) were added and ${exclusions.length} stock(s) were removed.`
        },
        {
            q: `Which stocks were added to ${formattedIndexName} on ${friendlyDate}?`,
            a: inclusions.length > 0
                ? `The following stocks were included in the ${formattedIndexName} index during this cycle: ${incListStr}.`
                : `No new stocks were added to the ${formattedIndexName} index during the ${friendlyDate} rebalancing.`
        },
        {
            q: `Which stocks were removed from ${formattedIndexName} on ${friendlyDate}?`,
            a: exclusions.length > 0
                ? `The following stocks were excluded from the ${formattedIndexName} index during this cycle: ${excListStr}.`
                : `No stocks were removed from the ${formattedIndexName} index during the ${friendlyDate} rebalancing.`
        },
        {
            q: `How can I download the complete constituents list of ${formattedIndexName} for ${friendlyDate}?`,
            a: `You can download the full, survivorship-bias-free constituent stock list of ${formattedIndexName} as of ${friendlyDate} in CSV format directly by clicking the 'Download Constituents CSV' button at the top of this page.`
        }
    ];

    // 1. Render FAQs visually on page
    const faqGrid = document.getElementById('faqGridContainer');
    if (faqGrid) {
        faqGrid.innerHTML = faqs.map(faq => `
            <div class="faq-item">
                <h3 class="faq-question">${escHtml(faq.q)}</h3>
                <p class="faq-answer">${escHtml(faq.a)}</p>
            </div>
        `).join('');
    }

    // 2. Inject FAQPage JSON-LD Schema
    const faqSchema = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': faqs.map(faq => ({
            '@type': 'Question',
            'name': faq.q,
            'acceptedAnswer': {
                '@type': 'Answer',
                'text': faq.a
            }
        }))
    };

    let faqScript = document.head.querySelector('#ld-faq');
    if (!faqScript) {
        faqScript = document.createElement('script');
        faqScript.id = 'ld-faq';
        faqScript.type = 'application/ld+json';
        document.head.appendChild(faqScript);
    }
    faqScript.text = JSON.stringify(faqSchema, null, 2);
}
