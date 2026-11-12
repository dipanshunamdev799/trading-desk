import dataMapMoObj from './constant.js';
import { secureApi } from './secureApi.js';

let linkval;
let linkvalmo;
if (
  window.location.origin.includes('beta.')
  || window.location.origin.includes('www.')
  || window.location.origin.includes('stage.')
  || window.location.origin.includes('motilal-mf-main')
) {
  linkval = 'https://contentapi.motilaloswalmf.com';
} else {
  linkval = 'https://uat-api.motilaloswalmf.com';
}

if (
  window.location.origin.includes('beta.')
  || window.location.origin.includes('www.')
  || window.location.origin.includes('stage.')
  || window.location.origin.includes('motilal-mf-main')
) {
  linkvalmo = 'https://moamcmob.motilaloswalmf.com';
} else {
  linkvalmo = 'https://api.moamc.com';
}

let linkvalport = 'https://mf.moamc.com';
if (window.location.origin.includes('beta.')
  || window.location.origin.includes('www.')
  || window.location.origin.includes('stage.')
  || window.location.origin.includes('motilal-mf-main')) {
  linkvalport = 'https://digital.motilaloswalmf.com';
}

export async function getbrowserNavigator() {
  const x = window.localStorage.getItem('mytime');

  let finalData = '';
  if (x === null) {
    const dataset = Date.now().toString(36) + Math.random().toString(36);
    window.localStorage.setItem('mytime', dataset);
    finalData = dataset;
  } else {
    finalData = x;
  }
  const Sys = {};
  const ua = window.navigator.userAgent.toLowerCase();
  let s;
  (s = ua.match(/msie ([\d.]+)/))
    ? (Sys.ie = s[1])
    : (s = ua.match(/firefox\/([\d.]+)/))
      ? (Sys.firefox = s[1])
      : (s = ua.match(/chrome\/([\d.]+)/))
        ? (Sys.chrome = s[1])
        : (s = ua.match(/opera.([\d.]+)/))
          ? (Sys.opera = s[1])
          : (s = ua.match(/version\/([\d.]+).*safari/))
            ? (Sys.safari = s[1])
            : 0;
  let keyData = '';
  if (Sys.ie !== undefined) {
    keyData = Sys.ie;
  }
  if (Sys.firefox !== undefined) {
    keyData = Sys.firefox;
  }
  if (Sys.chrome !== undefined) {
    keyData = Sys.chrome;
  }
  if (Sys.opera !== undefined) {
    keyData = Sys.opera;
  }
  if (Sys.safari !== undefined) {
    keyData = Sys.safari;
  }

  return finalData; // keyData.replaceAll(".", "").toString();
}

const appConfig = {
  'api-endpoints': {
    'upload-file': `${linkvalport}/ncms/api/ComparePortfolio/user-data-upload`,
    'get-user-data': `${linkvalport}/ncms/api/ComparePortfolio/get-user-data`,
    'add-user-data': `${linkvalport}/ncms/api/ComparePortfolio/add-user-data`,
    'delete-user-data': `${linkvalport}/ncms/api/ComparePortfolio/delete-user-data`,
    'get-cp-summary': `${linkvalport}/ncms/api/ComparePortfolio/get-cp-summary`,
    'get-companies': `${linkvalport}/ncms/api/ComparePortfolio/get-company-list`,
    'get-benchmarks': `${linkvalport}/ncms/api/ComparePortfolio/get-benchmark-list`,
    'get-schemes': `${linkvalport}/ncms/api/ComparePortfolio/get-scheme-list`,
  },
  'unique-ids': {
    'bulk-upload': await getbrowserNavigator(),
    // 'mmtx3b6m0.rd3pvxt2vvm',
    'manual-update': await getbrowserNavigator(),
    // 'mlj0nfkx0.uzmoq2yx8r',
  },
  'css-classes': {
    hidden: 'hidden-initially',
    error: 'error',
  },
  'file-accept': '.xlsx,.xls,.csv',
  'file-types': ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'],
  'file-extensions': ['.xlsx', '.xls', '.csv'],
};


const Listing = `${linkval}/api/public/v1/funds/listing`;

let cvlKycCheckQueue = Promise.resolve();
const pendingCvlKycChecks = new Map();

export function getCvlKycCheck(panNo, isNRI = false, isLogin = false) {
  const requestKey = `${panNo}:${isNRI}:${isLogin}`;
  const pendingRequest = pendingCvlKycChecks.get(requestKey);
  if (pendingRequest) return pendingRequest;

  const request = cvlKycCheckQueue.then(() => secureApi(
    `${linkvalmo}/initApi/api/Init/CVLKYCCheck`,
    {
      method: 'POST',
      body: { panNo, prelogin: true, isNRI, ...(isLogin ? { isLogin: true } : {}) },
      encryptRequest: false,
    },
  ));

  cvlKycCheckQueue = request.catch(() => undefined);
  pendingCvlKycChecks.set(requestKey, request);
  request
    .finally(() => pendingCvlKycChecks.delete(requestKey))
    .catch(() => undefined);
  return request;
}

export async function getKycStatus(request, headers = {}) {
  return secureApi(`${linkvalmo}/initApi/api/Init/GetKYCStatus`, {
    method: 'POST',
    body: request,
    headers,
    encryptRequest: false,
  });
}

export async function pushKraHit(request, headers = {}) {
  return secureApi(`${linkvalmo}/initApi/api/Init/PushKRAHit`, {
    method: 'POST',
    body: request,
    headers,
    encryptRequest: false,
  });
}

export async function lmsentCall(paramData) {
  const request = {
    frmdata: `LMS~${paramData.userLogPan}|${paramData.userLogPanNm}|+91${paramData.userLogMoNm}|${paramData.userLogEm}||${paramData.userCity || paramData.usercity || 'Mumbai'
      }||${paramData.kycflag}|MF New investor|||||||||${paramData.isnri}|`,
    prelogin: true,
  };

  return secureApi(`${linkvalmo}/initApi/api/Init/Lmsentry`, {
    method: 'POST',
    body: request,
    encryptRequest: false,
  });
}

export async function submitKycProcess(request, headers = {}) {
  return secureApi(`${linkvalmo}/prelogin/api/KYC/KYCProcess`, {
    method: 'POST',
    body: request,
    headers,
    encryptRequest: false,
  });
}

export async function getKycData(panNo) {
  return secureApi(`${linkvalmo}/prelogin/api/KYC/GetKYCData`, {
    method: 'POST',
    body: { panNo, prelogin: true },
    encryptRequest: false,
  });
}

export async function saveOtpPreference(request) {
  return secureApi(`${linkvalmo}/loginapi/api/Login/SaveOtpPreference`, {
    method: 'POST',
    body: request,
    encryptRequest: false,
  });
}

export async function getOtpPreferenceAvailability(request) {
  return secureApi(`${linkvalmo}/loginapi/api/Login/GetOTPPreferenceAvailability`, {
    method: 'POST',
    body: request,
    encryptRequest: false,
  });
}

export async function getPostLoginOtpPreferenceAvailability(panNo) {
  return secureApi(`${linkvalmo}/PostLogin/api/OTPPreference/GetOTPPreferenceAvailability`, {
    method: 'POST',
    body: { Panno: panNo, prelogin: true },
    encryptRequest: false,
  });
}

export async function getPostLoginContactDetails(panNo) {
  return secureApi(`${linkvalmo}/PostLogin/api/OTPPreference/GetContactDetailsForOTPPreference`, {
    method: 'POST',
    body: { Panno: panNo, prelogin: true },
    encryptRequest: false,
  });
}

export async function savePostLoginOtpPreference(request) {
  return secureApi(`${linkvalmo}/PostLogin/api/OTPPreference/SaveOtpPreference`, {
    method: 'POST',
    body: request,
    encryptRequest: false,
  });
}

export async function submitPanDetail(request) {
  return secureApi(`${linkvalmo}/MFTransaction/api/InvestorDetails/panDetail`, {
    method: 'POST',
    body: request,
    encryptRequest: false,
  });
}

export async function getClientType(panNo, includePrelogin = true) {
  return secureApi(`${linkvalmo}/LoginAPI/api/Login/GetClientType`, {
    method: 'POST',
    body: includePrelogin ? { panNo, prelogin: true } : { panNo },
    encryptRequest: false,
  });
}

export async function setMpin(request, headers = {}) {
  return secureApi(`${linkvalmo}/loginapi/api/Login/SETMPIN`, {
    method: 'POST',
    body: request,
    headers,
    encryptRequest: false,
  });
}

export async function authenticateUserCredentials(request, headers = {}) {
  return secureApi(`${linkvalmo}/loginapi/api/Login/AuthenticateUserCred`, {
    method: 'POST',
    body: request,
    headers,
    encryptRequest: false,
  });
}

export async function authenticateOtp(request, headers = {}) {
  return secureApi(`${linkvalmo}/loginapi/api/Login/AuthenticateUserCred`, {
    method: 'POST',
    body: request,
    headers,
    encryptRequest: false,
  });
}

export async function generateLoginOtp(request, headers = {}) {
  return secureApi(`${linkvalmo}/loginapi/api/Login/GenerateOtpNew`, {
    method: 'POST',
    body: request,
    headers,
    encryptRequest: false,
  });
}

export async function generateForgotPasscodeOtp(request, headers = {}) {
  return secureApi(`${linkvalmo}/loginapi/api/Login/GenrateMPINOTPValidate`, {
    method: 'POST',
    body: request,
    headers,
    encryptRequest: false,
  });
}

export async function initiateToken(bodyparam, headerparam) {
  const initiateResponse = await secureApi(
    `${linkvalmo}/loginapi/api/handoff/initiate`,
    {
      method: 'POST',
      body: bodyparam,
      headers: headerparam,
      encryptRequest: false,
    },
  );
  return initiateResponse;
}

export async function myAPI(method, url, body = null, customHeaders = {}) {
  try {
    const options = { method };

    const headers = { ...customHeaders };
    // headers.appid = "A1B37471M28A2A4178MB233C73FA0AB74DF2";

    if (body) {
      // 2. Check if body is FormData
      if (body instanceof FormData) {
        // Do NOT stringify FormData
        options.body = body;

        // CRITICAL: Remove 'Content-Type'.
        // Let the browser set it to "multipart/form-data; boundary=..."
        if (headers['Content-Type']) {
          delete headers['Content-Type'];
        }
      } else {
        // 3. Handle JSON Body
        // if (typeof body === 'string') {
        //   options.body = JSON.stringify({
        //     'body':body,
        //   });
        // } else {
        // }
        options.body = JSON.stringify(body);

        // Ensure Content-Type is JSON (if not overridden by customHeaders)
        if (!headers['Content-Type']) {
          headers['Content-Type'] = 'application/json';
        }
      }
    }

    // 4. Assign the sanitized headers object to options
    options.headers = headers;

    const response = await fetch(url, options);

    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    const text = await response.text();
    try {
      return JSON.parse(text);
    } catch (e) {
      return text;
    }
  } catch (error) {
    // error handling
    return null;
  }
}

export function generateAppId() {
  const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVXYZ';
  let appId = '';
  for (let i = 0; i < 36; i += 1) {
    appId += chars[Math.floor(Math.random() * chars.length)];
  }
  return appId;
}

// Lazy-loaded placeholder for publisherUrl - only fetched when needed
let placeholderCache = null;
export async function getPublisherUrl() {
  if (!placeholderCache) {
    const { fetchPlaceholders } = await import('./aem.js');
    placeholderCache = await fetchPlaceholders();
  }
  return placeholderCache.publisherUrl;
}

/* ---------------- DOM Instrumentation Utilities ---------------- */
export function moveAttributes(from, to, attributes) {
  let attrs = attributes;
  if (!attrs) {
    attrs = [...from.attributes].map(({ nodeName }) => nodeName);
  }
  attrs.forEach((attr) => {
    const value = from.getAttribute(attr);
    if (value) {
      to.setAttribute(attr, value);
      from.removeAttribute(attr);
    }
  });
}

export function moveInstrumentation(from, to) {
  moveAttributes(
    from,
    to,
    [...from.attributes]
      .map(({ nodeName }) => nodeName)
      .filter(
        (attr) => attr.startsWith('data-aue-') || attr.startsWith('data-richtext-'),
      ),
  );
}

/* ---------------- Intersection Observer ---------------- */
export function initObserver(block, callback) {
  const observer = new IntersectionObserver((entries, obs) => {
    if (entries.some((e) => e.isIntersecting)) {
      obs.disconnect();
      callback();
    }
  });
  observer.observe(block);
}

/* ---------------- Fund Listings API ---------------- */
// Session-level cache key for the fund listing. The in-memory cache
// (dataMapMoObj.fundListings) only lives for one page; since this site is a
// full-page-reload (EDS) site, navigating to another page resets it and would
// re-fetch. sessionStorage persists the listing for the whole browser tab/
// session, so the listing API is called only ONCE per session and reused on
// every subsequent page (header reload) until the tab is closed.
const FUND_LISTINGS_SESSION_KEY = 'moamc_fund_listings';
// Validity window for the cached fund listing: 12 hours.
//
// The listing is persisted in sessionStorage together with the timestamp at
// which it was fetched. On every read we compare `Date.now()` against that
// timestamp; if more than 12 hours have elapsed the cached copy is treated as
// expired — it is removed and a fresh listing is fetched (and re-cached with a
// new timestamp). This bounds how stale the listing can get within a single
// long-lived browser tab. (sessionStorage itself is also cleared when the tab
// is closed, so 12 hours is the upper bound, not a guaranteed lifetime.)
const FUND_LISTINGS_TTL_MS = 12 * 60 * 60 * 1000; // 12 hours in milliseconds
let fundListingsPromise = null;

export async function getFundListings() {
  // 1) In-memory cache (same page).
  if (dataMapMoObj.fundListings) {
    return dataMapMoObj.fundListings;
  }

  // 2) sessionStorage cache (survives page navigations within the tab), valid
  //    for FUND_LISTINGS_TTL_MS (12 hours). A cache older than that, or one in a
  //    legacy format without a timestamp, is discarded and re-fetched below.
  try {
    const cached = sessionStorage.getItem(FUND_LISTINGS_SESSION_KEY);
    if (cached) {
      const parsed = JSON.parse(cached);
      // Fresh only when a numeric timestamp exists and is within the 12h window.
      const isFresh = parsed
        && typeof parsed.timestamp === 'number'
        && (Date.now() - parsed.timestamp) < FUND_LISTINGS_TTL_MS;
      if (isFresh && parsed.data) {
        dataMapMoObj.fundListings = parsed.data;
        return parsed.data;
      }
      // Expired (older than 12h) or malformed (e.g. legacy entry without a
      // timestamp) — drop it so the network fetch below refreshes the cache.
      sessionStorage.removeItem(FUND_LISTINGS_SESSION_KEY);
    }
  } catch (e) {
    // Ignore storage/parse errors and fall through to the network fetch.
  }

  // 3) De-dupe concurrent callers within the same page: reuse one in-flight
  //    request instead of firing multiple listing calls.
  if (fundListingsPromise) {
    return fundListingsPromise;
  }

  fundListingsPromise = (async () => {
    try {
      const data = await secureApi(Listing, { method: 'GET' });
      dataMapMoObj.fundListings = data;
      try {
        // Persist the listing with the fetch time so the read path can enforce
        // the 12-hour validity window (see FUND_LISTINGS_TTL_MS above).
        sessionStorage.setItem(
          FUND_LISTINGS_SESSION_KEY,
          JSON.stringify({ data, timestamp: Date.now() }),
        );
      } catch (e) {
        // sessionStorage may be full/unavailable — safe to ignore; the
        // in-memory cache still prevents duplicate calls on this page.
      }
      return data;
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error fetching fund listings:', error);
      throw error;
    } finally {
      fundListingsPromise = null;
    }
  })();

  return fundListingsPromise;
}

export async function getDownloadsDropdownOptions(type) {
  let origin = window.location.origin;
  if (
    origin.includes('motilaloswalamc')
    || origin.includes('main--motilal-mf')
    || origin.includes('main--motilal-amc')
  ) {
    origin = origin.replace('amc', 'mf');
  }
  if (
    window.location.pathname.includes('motilal-mf')
    || window.location.pathname.includes('motilal-amc')
  ) {
    origin = 'https://dev.motilaloswalmf.com';
  }

  const url = `${origin}/content/aem-cloud-dept-backend-motilal-oswal/api/downloads-dropdown-options.json?type=${encodeURIComponent(type || '')}`;
  return myAPI('GET', url);
}

export async function searchDownloadResults(params = {}) {
  let origin = window.location.origin;
  if (
    origin.includes('motilaloswalamc')
    || origin.includes('main--motilal-mf')
    || origin.includes('main--motilal-amc')
  ) {
    origin = origin.replace('amc', 'mf');
  }
  if (
    window.location.pathname.includes('motilal-mf')
    || window.location.pathname.includes('motilal-amc')
  ) {
    origin = 'https://dev.motilaloswalmf.com';
  }

  const url = `${origin}/content/aem-cloud-dept-backend-motilal-oswal/api/search-documents.json?searchQuery=${params.searchQuery || ''}&type=${params.type || ''}&category=${params.category || ''}`;
  return myAPI('GET', url);
}

export async function searchDownloadDocuments(params = {}, isSummary = false) {
  let origin = window.location.origin;
  if (
    origin.includes('motilaloswalamc')
    || origin.includes('main--motilal-mf')
    || origin.includes('main--motilal-amc')
  ) {
    origin = origin.replace('amc', 'mf');
  }
  if (
    window.location.pathname.includes('motilal-mf')
    || window.location.pathname.includes('motilal-amc')
  ) {
    origin = 'https://dev.motilaloswalmf.com';
  }

  const url = `${origin}/content/aem-cloud-dept-backend-motilal-oswal/api/search-documents.json?year=${params.year || ''}&category=${params.category || ''}&month=${params.month || ''}&type=${params.type || ''}`;
  return myAPI('GET', url);
}

export async function getAuthorIndex() {
  return secureApi(`${window.location.origin}/query-index-moedge.json`, {
    method: 'GET',
    encryptRequest: false,
  });
}

export async function getInvestorIndex() {
  return secureApi(`${window.location.origin}/query-index-investor.json`, {
    method: 'GET',
    encryptRequest: false,
  });
}

export async function getScheme(schemeCode) {
  return secureApi(`${linkval}/api/public/v1/funds?schcode=${schemeCode}`, {
    method: 'GET',
    encryptRequest: false,
  });
}

export async function getFundManager(schemeCode) {
  return secureApi(`${linkval}/api/public/v1/funds/manager?schcode=${schemeCode}`, {
    method: 'GET',
    encryptRequest: false,
  });
}

export async function getPmsScheme(schemeCode) {
  return secureApi(`${linkval}/api/public/v1/pms?schcode=${schemeCode}`, {
    method: 'GET',
    encryptRequest: false,
  });
}

export async function getPerformanceGraph(payload) {
  return secureApi('https://www.motilaloswalmf.com/mutualfund/api/v1/PerformanceGraphNew', {
    method: 'POST',
    body: payload,
    encryptRequest: false,
  });
}

export async function getPerformanceGraphLumpsum(payload, headers = {}) {
  return secureApi(
    `${linkvalmo}/PreLogin/api/SchemeDetails/GetPerformanceGraphLumpsum`,
    {
      method: 'POST',
      body: payload,
      headers,
      encryptRequest: false,
    },
  );
}

// Maps a single row from the new RiskReturnsMF API (camelCase keys) to the
// legacy shape the risk-adjusted-return table rendering code expects.
function normaliseRiskReturnRow(row = {}) {
  return {
    schemeCode: row.schemeCode,
    schemeName: row.schemeName,
    benchmarkName: row.benchmarkName,
    schemeRisk: row.schemeRisk,
    benchmarkRisk: row.benchmarkRisk,
    navRecdt: row.navDate,
    regularNav: row.navRegular,
    directNav: row.navDirect,
    '1yrregular': row.yr1Regular,
    '1yrdirect': row.yr1Direct,
    '1yrbm': row.yr1Bm,
    '1yrirregular': row.yr1IrRegular,
    '1yrirdirect': row.yr1IrDirect,
    '3yrregular': row.yr3Regular,
    '3yrdirect': row.yr3Direct,
    '3yrbm': row.yr3Bm,
    '3yrirregular': row.yr3IrRegular,
    '3yrirdirect': row.yr3IrDirect,
    '5yrregular': row.yr5Regular,
    '5yrdirect': row.yr5Direct,
    '5yrbm': row.yr5Bm,
    '5yrirregular': row.yr5IrRegular,
    '5yrirdirect': row.yr5IrDirect,
    '10yrregular': row.yr10Regular,
    '10yrdirect': row.yr10Direct,
    '10yrbm': row.yr10Bm,
    '10yrirregular': row.yr10IrRegular,
    '10yrirdirect': row.yr10IrDirect,
    siregular: row.siRegular,
    sidirect: row.siDirect,
    sibm: row.siBm,
    dailyaum: row.dailyAum,
    // New API has no date-of-allotment; riskReturnDate keeps the sort stable.
    dtofalotment: row.riskReturnDate,
  };
}

export async function getRiskReturns(payload) {
  const resp = await secureApi(
    `${linkvalport}/stage/ncms/api/RiskReturnsMF/get-risk-returns`,
    {
      method: 'POST',
      body: payload,
      encryptRequest: false,
    },
  );

  // New API envelope: { code, response: { latest, historical }, message }.
  // Legacy callers expect { data: { latest, historical } } with legacy field
  // names, so normalise here and keep the rest of the UI code unchanged.
  const source = resp?.response || {};
  const mapList = (list) => (Array.isArray(list) ? list.map(normaliseRiskReturnRow) : []);

  return {
    ...resp,
    data: {
      latest: mapList(source.latest),
      historical: mapList(source.historical),
    },
  };
}

export async function getSchemeDetails(schemeCode) {
  try {
    const url = `${linkval}/api/public/v1/funds?schcode=${schemeCode}`;
    const data = await secureApi(url, { method: 'GET', encryptRequest: false });
    return data;
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(`Error fetching scheme details for ${schemeCode}:`, error);
    throw error;
  }
}

export async function deleteUserData(recordId, uniqueId) {
  return secureApi(appConfig['api-endpoints']['delete-user-data'], {
    method: 'POST',
    body: {
      RecordId: parseInt(recordId, 10),
      uniqueId,
    },
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

/**
 * Delete ALL compare-portfolio records for a given browser identity.
 * Sends RecordId as null and hasDeleteAllRecord true. The uniqueId is the
 * value stored in localStorage under the `mytime` key (see getbrowserNavigator).
 * Example: deleteAllUserData(localStorage.getItem('mytime'));
 */
export async function deleteAllUserData(uniqueId) {
  return secureApi(appConfig['api-endpoints']['delete-user-data'], {
    method: 'POST',
    body: {
      RecordId: null,
      uniqueId,
      hasDeleteAllRecord: true,
    },
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

export async function uploadUserData(file, uniqueId) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('uniqueId', uniqueId);

  return secureApi(appConfig['api-endpoints']['upload-file'], {
    method: 'POST',
    body: formData,
    headers: { 'x-encrypted': 'N' },
    encryptRequest: false,
  });
}

export async function getUserData(uniqueId) {
  return secureApi(appConfig['api-endpoints']['get-user-data'], {
    method: 'POST',
    body: { uniqueId },
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

export async function getCompanyList() {
  return secureApi(appConfig['api-endpoints']['get-companies'], {
    method: 'POST',
    body: {},
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

export async function getBenchmarkList() {
  return secureApi(appConfig['api-endpoints']['get-benchmarks'], {
    method: 'POST',
    body: {},
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

export async function getSchemeList() {
  return secureApi(appConfig['api-endpoints']['get-schemes'], {
    method: 'POST',
    body: {},
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

export async function addUserData(uniqueId, isin, noOfShare) {
  return secureApi(appConfig['api-endpoints']['add-user-data'], {
    method: 'POST',
    body: {
      uniqueId,
      isin,
      noOfShare: parseInt(noOfShare, 10),
    },
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

export async function getCpSummary(payload) {
  return secureApi(appConfig['api-endpoints']['get-cp-summary'], {
    method: 'POST',
    body: payload,
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

export async function getCpSummaryPdf(payload) {
  return secureApi(`${linkvalport}/ncms/api/ComparePortfolio/get-cp-summary-pdf`, {
    method: 'POST',
    body: payload,
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

// export async function getPerformanceGraphLumpsum(payload, headers = {}) {
//   return secureApi(`${linkvalmo}/PreLogin/api/SchemeDetails/GetPerformanceGraphLumpsum`, {
//     method: 'POST',
//     body: payload,
//     headers,
//     encryptRequest: false,
//   });
// }

export async function removeCart(cartId, headers = {}) {
  return secureApi(`${linkvalport}/oms/api/Cart/prelogin-remove-cart?cartId=${cartId}`, {
    method: 'GET',
    headers,
    encryptRequest: false,
  });
}

export async function addCart(payload, headers = {}) {
  return secureApi(`${linkvalport}/oms/api/Cart/prelogin-add-to-cart`, {
    method: 'POST',
    body: payload,
    headers,
    encryptRequest: false,
  });
}

export async function getCartDetails(cartId, headers = {}) {
  return secureApi(
    `${linkvalport}/oms/api/Cart/prelogin-get-cart-details?cartId=${cartId}`,
    {
      method: 'GET',
      headers,
      encryptRequest: false,
    },
  );
}

export async function validateFolioArnPanMapping(formData, product = 'MF') {
  const endpoint = product === 'PMS'
    ? `${linkvalmo}/PMS/api/Reports/ValidateStrategyARNPanMapping`
    : `${linkvalmo}/prelogin/api/ReportUtility/ValidateFolioARNPanMapping`;

  return secureApi(endpoint, {
    method: 'POST',
    body: formData,
    encryptRequest: false,
  });
}

export async function generateMFReports(payload) {
  return secureApi(`${linkvalmo}/prelogin/api/ReportUtility/GenerateMFReports`, {
    method: 'POST',
    body: payload,
    encryptRequest: false,
  });
}

export async function generateAIFReports(payload) {
  return secureApi(`${linkvalmo}/prelogin/api/ReportUtility/GenerateAIFReports`, {
    method: 'POST',
    body: payload,
    encryptRequest: false,
  });
}

export async function generatePMSReports(payload) {
  return secureApi(`${linkvalmo}/PMS/api/Reports/GetDITPMSReportsSendEmail`, {
    method: 'POST',
    body: payload,
    encryptRequest: false,
  });
}

export async function verifyLeadOtp(leadId, otp) {
  return secureApi(`${linkvalmo}/LMS/api/Lead/VerifyOTP`, {
    method: 'POST',
    body: {
      leadId: Number(leadId),
      otp: Number(otp),
      _nextType: '/VerifyOTP',
    },
    encryptRequest: false,
    headers: {
      'Content-Type': 'application/json',
      useragent: 'WEB/LEADCAMPAIGN',
    },
  });
}

export async function saveRawLead(payload, headers = {}) {
  return secureApi(`${linkvalmo}/LMS/api/Lead/SaveRawLead`, {
    method: 'POST',
    body: payload,
    headers,
    encryptRequest: false,
  });
}

export async function getComparePortfolioList(endpoint) {
  return secureApi(endpoint, {
    method: 'POST',
    body: {},
    headers: {
      'Content-Type': 'application/json',
      'x-encrypted': 'N',
    },
    encryptRequest: false,
  });
}

export async function calculateFabCashFlow(investmentType, payload) {
  const endpoint = investmentType === 'investment-amount'
    ? 'CashFlowCalculatorFrequency'
    : 'CashFlowCalculatorExpenseFrequencyFAB';

  return secureApi(`${linkvalmo}/initapi/api/Init/${endpoint}`, {
    method: 'POST',
    body: payload,
    headers: { 'Content-Type': 'application/json' },
    encryptRequest: false,
  });
}

export async function getCobrandingDoc(payload) {
  return secureApi(`${linkvalmo}/initapi/api/Init/GetCobrandingDoc`, {
    method: 'POST',
    body: payload,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    encryptRequest: false,
  });
}

export async function getCobrandingDist(arnNo) {
  return secureApi(`${linkvalmo}/initapi/api/Init/GetCobrandingDist`, {
    method: 'POST',
    body: { arnNo },
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    encryptRequest: false,
  });
}

export async function getUnclaimedDetails(unclaimedtype, folioNo, accessToken = '') {
  const headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'WEB/MultipleCampaign',
    useragent: 'WEB/OTPLEADS',
  };

  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

  return secureApi(`${linkvalmo}/postlogin/api/Unclaimed/GetUnclaimedDetails`, {
    method: 'POST',
    body: { unclaimedtype, folioNo },
    headers,
    encryptRequest: false,
  });
}

export async function getUnclaimedFolioPan(payload) {
  return secureApi(`${linkvalmo}/postlogin/api/Unclaimed/GetUnclaimedFolioPan`, {
    method: 'POST',
    body: payload,
    encryptRequest: false,
  });
}

export async function searchContent(query) {
  const searchHost = window.location.origin.includes('beta.')
    || window.location.origin.includes('www.')
    ? 'https://contentapi.motilaloswalmf.com'
    : 'https://uat-api.motilaloswalmf.com';
  const url = `${searchHost}/api/public/v1/opensearch/searchContent?query=${encodeURIComponent(query)}`;

  return secureApi(url, {
    method: 'GET',
    encryptRequest: false,
  });
}

export async function getINAVAndPrice() {
  return secureApi('https://www.motilaloswalmf.com/mutualfund/api/v1/someFunc', {
    method: 'POST',
    body: { apiName: 'GetINAVandPrice' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'WEB/MultipleCampaign',
      useragent: 'WEB/MultipleCampaign',
      UserAgent: 'WEB/MultipleCampaign',
    },
    encryptRequest: false,
  });
}

export async function getEodUpdate() {
  return secureApi('https://www.motilaloswalmf.com/mutualfund/api/v1/someFunc', {
    method: 'POST',
    body: { apiName: 'GetEODUpdate' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'WEB/MultipleCampaign',
      'user-agent': 'WEB/MultipleCampaign',
      UserAgent: 'WEB/MultipleCampaign',
    },
    encryptRequest: false,
  });
}

export async function getMarketUpdate() {
  return secureApi('https://www.motilaloswalmf.com/mutualfund/api/v1/someFunc', {
    method: 'POST',
    body: { apiName: 'GetMarketUpdate' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'WEB/MultipleCampaign',
      'user-agent': 'WEB/MultipleCampaign',
      UserAgent: 'WEB/MultipleCampaign',
    },
    encryptRequest: false,
  });
}

export async function getBranchDetails(origin = window.location.origin) {
  const url = origin.includes('amc') || origin.includes('motilal-amc')
    ? 'https://www.motilaloswalamc.com/api/branch-details.json'
    : `${origin}/api/branch-details.json`;

  return secureApi(url, {
    method: 'GET',
    encryptRequest: false,
  });
}

export async function getTotalExpenseRatio() {
  return secureApi(
    'https://www.motilaloswalmf.com/content/aem-cloud-dept-backend-motilal-oswal/api/getTotalExpratio.json',
    {
      method: 'GET',
      encryptRequest: false,
    },
  );
}

export async function getTrackingError(schemeCode) {
  return secureApi(
    'https://moamcmob.motilaloswalmf.com/PreLogin/api/SchemeDetailsV2/GetTError',
    {
      method: 'POST',
      body: { schemeCode },
      headers: {
        'Content-Type': 'application/json',
        appid: '37F92DDEMBBE0A4F8EM9589CD5DC00656CD9',
        Cookie:
          'TS01621037=01f5407e93d8fff00a90f8fc29d21465a95235098342de5d91aac0ba1a2202e1beb58944c5a8ab3d2ccaa7980de5528f5b15c2a724; TS01621037=01f5407e93bf5d45e1b943d8d5eda28a5a807a0fd7d006eab25738450c78c9e8512a2114208b934539cd6fdf6f5cd20ecfa96e602f',
      },
      encryptRequest: false,
    },
  );
}

export async function getTrackingDifference(schemeCode) {
  return secureApi(
    'https://moamcmob.motilaloswalmf.com/prelogin/api/SchemeDetailsV2/GetTDifference',
    {
      method: 'POST',
      body: { schemeCode },
      headers: {
        'Content-Type': 'application/json',
        appid: '37F92DDEMBBE0A4F8EM9589CD5DC00656CD9',
        Cookie:
          'TS01621037=01f5407e93d8fff00a90f8fc29d21465a95235098342de5d91aac0ba1a2202e1beb58944c5a8ab3d2ccaa7980de5528f5b15c2a724; TS01621037=01f5407e935158b2625c260fd665f41ea70e3655815acd8cc2b179ae8db7571d7752b83e0076698d2cdf26f1251a44688fde1289bd; TS01621037=01f5407e93a4b1465144bb691a162d023d6a7fcd1076ea5901cd1251cf6c26e550100633148e468a55d17f5d30d7dd755acbc26c1e',
      },
      encryptRequest: false,
    },
  );
}

export async function createLead(payload) {
  return secureApi('https://mf.moamc.com/ums/api/SaveLead/create-leads', {
    method: 'POST',
    body: payload,
    headers: {
      'Content-Type': 'application/json',
      appid: generateAppId(),
    },
    encryptRequest: false,
  });
}

export async function plholdersht() {
  if (dataMapMoObj.placeholderval) {
    return dataMapMoObj.placeholderval;
  }
  try {
    const { getPlaceholderCall } = await import('./encryptAndDecryptHelper.js');
    const data = await getPlaceholderCall();
    dataMapMoObj.placeholderval = data;
    return data;
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error('Error fetching fund placeholderval:', error);
    throw error;
  }
}
