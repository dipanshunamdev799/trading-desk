// our fund code
import {
  div,
  input,
  label,
  span,
  p,
  button,
  ul,
  li,
  a,
  img,
  h3,
  details,
  summary,
  table,
  thead,
  tbody,
  tr,
  th,
  td,
  strong,
  h2,
  fieldset,
  legend,
} from "../../scripts/dom-helpers.js";
import dataMapMoObj from "../../scripts/constant.js";
import fundcardblock from "../fund-card/fund-card.js";
import listviewblock from "../list-view-card/list-view-card.js";
import "../../scripts/flatpickr.js";
import {
  getDownloadsDropdownOptions,
  getFundListings,
  getRiskReturns,
  searchDownloadDocuments,
  searchDownloadResults,
} from "../../scripts/api.js";
import { showRegularPlanPopover } from "../../scripts/regular-plan-popover.js";

// Module-level cache for listing data
let listingData = null;

const ensureCancelButton = (element) => {
  if (!element) return null;
  if (element.tagName === "BUTTON") {
    if (!element.getAttribute("type")) {
      element.setAttribute("type", "button");
    }
    if (!element.getAttribute("aria-label")) {
      element.setAttribute("aria-label", "Clear search");
    }
    return element;
  }

  const btn = document.createElement("button");
  btn.className = element.className;
  btn.setAttribute("type", "button");

  Array.from(element.attributes).forEach((attr) => {
    if (attr.name === "class") return;
    btn.setAttribute(attr.name, attr.value);
  });

  if (!btn.getAttribute("aria-label")) {
    btn.setAttribute("aria-label", "Clear search");
  }

  while (element.firstChild) {
    btn.appendChild(element.firstChild);
  }

  element.replaceWith(btn);
  return btn;
};

function getFundStatus(fund) {
  const now = new Date();

  // Extract date strings
  const nfoStartStr = fund?.schDetail?.nfoStartDate;
  const nfoEndStr = fund?.schDetail?.nfoEndDate;
  const reopenStr = fund?.nfoReopenDate;

  // Initialize NFO Start Date
  const nfoStart = nfoStartStr ? new Date(nfoStartStr) : null;

  // 🔄 Handle Assumption: NFO End Date and Reopen Date are the same if one is missing
  const nfoEnd = nfoEndStr
    ? new Date(nfoEndStr)
    : reopenStr
      ? new Date(reopenStr)
      : null;

  const reopen = reopenStr
    ? new Date(reopenStr)
    : nfoEndStr
      ? new Date(nfoEndStr)
      : null;

  // 🔒 Normalize NFO start date to START OF DAY
  if (nfoStart) {
    nfoStart.setHours(0, 0, 0, 0);
  }

  // 🔒 Normalize NFO end date to END OF DAY
  if (nfoEnd) {
    nfoEnd.setHours(23, 59, 59, 999);
  }

  // 🔒 Normalize reopen date to START OF DAY
  if (reopen) {
    reopen.setHours(0, 0, 0, 0);
  }

  if (nfoStart && now < nfoStart) {
    return { isNFO: true, investEnabled: false };
  }
  if (nfoStart && !nfoEnd && !reopen && now >= nfoStart) {
    return { isNFO: true, investEnabled: true };
  }
  if (nfoStart && nfoEnd && now >= nfoStart && now <= nfoEnd) {
    return { isNFO: true, investEnabled: true };
  }
  if (nfoEnd && reopen && now > nfoEnd && now < reopen) {
    return { isNFO: true, investEnabled: false };
  }
  if (nfoEnd && reopen && now < nfoEnd && now < reopen) {
    return { isNFO: true, investEnabled: false };
  }
  if (reopen && now >= reopen) {
    return { isNFO: false, investEnabled: true };
  }

  // 5️⃣ Fallback
  return { isNFO: false, investEnabled: true };
}

function dataFilterfun(param) {
  let nforemove = "";
  let nfoscheme = "";
  const dataMapObj = {
    schemeName: [],
    fundCategory: [
      {
        nfo: [],
      },
      {
        "indian-equity": [],
      },
      {
        "international-equity": [],
      },
      {
        "hybrid-&-balanced": [],
      },
      {
        "multi-asset": [],
      },
      {
        commodity: [],
      },
      {
        "debt-&-liquid": [],
      },
      {
        indianEquitySub: [
          {
            "large-and-mid-cap": [],
          },
          {
            "large-cap": [],
          },
          {
            "mid-cap": [],
          },
          {
            "small-cap": [],
          },
          {
            sector: [],
          },
          {
            factor: [],
          },
          {
            "tax-saver-(elss)": [],
          },
          {
            "multi-cap-fund": [],
          },
          {
            "flexi-cap": [],
          },
          {
            "contra": [],
          },
        ],
      },
    ],
    fundType: [
      {
        active: [],
      },
      {
        "index-funds": [],
      },
      {
        etf: [],
      },
    ],
    sort: [
      {
        ListDropdown: [
          {
            text: "Popular",
            value: "inception_Ret",
          },
          {
            text: "1 Year Returns",
            value: "oneYear_Ret",
          },
          {
            text: "3 Year Returns",
            value: "threeYear_Ret",
          },
          {
            text: "5 Year Returns",
            value: "fiveYear_Ret",
          },
          {
            text: "7 Year Returns",
            value: "sevenYear_Ret",
          },
          {
            text: "10 Year Returns",
            value: "tenYear_Ret",
          },
        ],
        inception_Ret: [],
        oneYear_Ret: [],
        threeYear_Ret: [],
        fiveYear_Ret: [],
        sevenYear_Ret: [],
        tenYear_Ret: [],
      },
    ],
  };

  const { fundCategory } = dataMapObj;
  const { fundType } = dataMapObj;
  const fundSort = dataMapObj.sort[0];
  const equitySub = fundCategory[fundCategory.length - 1].indianEquitySub;

  const categoryMapKeys = [
    "motilal-oswal-amc:nfo",
    "motilal-oswal-amc:indian-equity-",
    "motilal-oswal-amc:international-equity",
    "motilal-oswal-amc:hybrid-&-balanced",
    "motilal-oswal-amc:multi-asset",
    "motilal-oswal-amc:commodity",
    "motilal-oswal-amc:debt-&-liquid",
  ];
  const categoryValues = [
    "nfo",
    "indian-equity",
    "international-equity",
    "hybrid-&-balanced",
    "multi-asset",
    "commodity",
    "debt-&-liquid",
  ];

  const typeMapKeys = [
    "motilal-oswal-amc:active",
    "motilal-oswal-amc:index-funds",
    "motilal-oswal-amc:etf",
  ];
  const typeValues = ["active", "index-funds", "etf"];

  const subcategoryMapKeys = [
    "motilal-oswal-amc:large-and-mid-cap",
    "motilal-oswal-amc:large-cap",
    "motilal-oswal-amc:mid-cap",
    "motilal-oswal-amc:small-cap",
    "motilal-oswal-amc:sector",
    "motilal-oswal-amc:factor",
    "motilal-oswal-amc:tax-saver-(elss)",
    "motilal-oswal-amc:multi-cap-fund",
    "motilal-oswal-amc:flexi-cap",
    "motilal-oswal-amc:contra"
  ];
  const subcategoryValues = [
    "large-and-mid-cap",
    "large-cap",
    "mid-cap",
    "small-cap",
    "sector",
    "factor",
    "tax-saver-(elss)",
    "multi-cap-fund",
    "flexi-cap",
    "contra"
  ];

  for (let i = 0; i < param.length; i += 1) {
    const name = param[i];
    const tags = name.fundsTaggingSection;
    const { schcode } = name;
    const nfofund = getFundStatus(name);
    if (nfofund.isNFO && nfofund.investEnabled) {
      nforemove = "Y";
    }

    if (nfofund.isNFO && !nfofund.investEnabled) {
      nfoscheme = name.schcode;
    }
    // Category matching
    for (let k = 0; k < categoryMapKeys.length; k += 1) {
      if (tags.indexOf(categoryMapKeys[k]) !== -1) {
        const category = categoryValues[k];
        if (category === "nfo" && !(nfofund.isNFO && nfofund.investEnabled)) {
          continue;
        }
        for (let j = 0; j < fundCategory.length; j += 1) {
          if (fundCategory[j][category]) {
            fundCategory[j][category].push(schcode);
            break;
          }
        }
      }
    }

    // Type matching
    for (let k = 0; k < typeMapKeys.length; k += 1) {
      if (tags.indexOf(typeMapKeys[k]) !== -1) {
        // const type = typeValues[k];
        if (schcode !== nfoscheme) {
          fundType[k][typeMapKeys[k].split(":")[1]].push(schcode);
        }
        // for (let j = 0; j < fundType.length; j += 1) {
        //   if (fundType[j][type]) {
        //     fundType[j][type].push(schcode);
        //     break;
        //   }
        // }
      }
    }

    // subCate matching
    for (let k = 0; k < subcategoryMapKeys.length; k += 1) {
      if (tags.indexOf(subcategoryMapKeys[k]) !== -1) {
        const type = subcategoryValues[k];
        for (let j = 0; j < equitySub.length; j += 1) {
          if (equitySub[j][type]) {
            equitySub[j][type].push(schcode);
            break;
          }
        }
      }
    }

    // Returns sorting
    const { returns } = name;
    if (returns && returns.length) {
      for (let r = 0; r < returns.length; r += 1) {
        const ret = returns[r];
        if (
          ret.inception_Ret &&
          fundSort.inception_Ret.indexOf(schcode) === -1
        ) {
          fundSort.inception_Ret.push(schcode);
        }
        if (ret.oneYear_Ret && fundSort.oneYear_Ret.indexOf(schcode) === -1) {
          fundSort.oneYear_Ret.push(schcode);
        }
        if (
          ret.threeYear_Ret &&
          fundSort.threeYear_Ret.indexOf(schcode) === -1
        ) {
          fundSort.threeYear_Ret.push(schcode);
        }
        if (ret.fiveYear_Ret && fundSort.fiveYear_Ret.indexOf(schcode) === -1) {
          fundSort.fiveYear_Ret.push(schcode);
        }
        if (
          ret.sevenYear_Ret &&
          fundSort.sevenYear_Ret.indexOf(schcode) === -1
        ) {
          fundSort.sevenYear_Ret.push(schcode);
        }
        if (ret.tenYear_Ret && fundSort.tenYear_Ret.indexOf(schcode) === -1) {
          fundSort.tenYear_Ret.push(schcode);
        }
      }
    }

    const sh = schcode;
    // Scheme Name
    dataMapObj.schemeName.push({
      schemeName: name.schemeName,
      schcode: sh,
    });
  }
  if (nforemove === "") {
    dataMapObj.fundCategory = dataMapObj.fundCategory.filter(
      (el) => Object.keys(el)[0] !== "nfo",
    );
  }
  return dataMapObj;
}

function capitalizeEachWord(sentence) {
  if (sentence.includes("etf")) {
    return `${sentence.toUpperCase()}'s`;
  }
  return sentence.replace(/\b\w/g, (char) => char.toUpperCase());
}

function updateClearallButtonState(block) {
  const clearallBtn = block.querySelector(".clearall-btn");
  if (!clearallBtn) return;

  const filterInputs = block.querySelectorAll(
    '.filter-list-wrapper input[type="checkbox"]',
  );
  const hasActiveFilters = Array.from(filterInputs).some(
    (inputval) => inputval.checked,
  );

  if (hasActiveFilters) {
    clearallBtn.classList.add("has-filters");
    // console.log('✅ Filters added - clearall-btn has-filters class added');
  } else {
    clearallBtn.classList.remove("has-filters");
    // console.log('❌ No filters - clearall-btn has-filters class removed');
  }
}

const returnPeriodFallbacks = [
  "tenYear_Ret",
  "sevenYear_Ret",
  "fiveYear_Ret",
  "threeYear_Ret",
  "oneYear_Ret",
  "inception_Ret",
];

const getBestAvailableReturn = (fund, targetPlanName, preferredKey) => {
  const planCode = fund?.planList?.find(
    (plan) => plan.planName === targetPlanName,
  )?.planCode;
  const returnObj = fund?.returns?.find((ret) => ret.plancode === planCode)
    || fund?.returns?.[0];
  const periodKeys = [
    preferredKey,
    ...returnPeriodFallbacks.filter((key) => key !== preferredKey),
  ];

  for (const key of periodKeys) {
    const value = parseFloat(returnObj?.[key]);
    if (!Number.isNaN(value) && value !== 0) {
      return value;
    }
  }
  return 0;
};

const appendUniqueFunds = (funds, additionalFunds) => {
  const seen = new Set();
  return [...funds, ...additionalFunds].filter((fund) => {
    const key = fund?.schcode || fund?.schemeName;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
};

const orderNonEtfFirst = (funds) => {
  if (!Array.isArray(funds)) return [];
  const nfoFunds = funds.filter((fund) =>
    fund?.fundsTaggingSection?.includes("motilal-oswal-amc:nfo"),
  );
  const nonNfoFunds = funds.filter(
    (fund) => !fund?.fundsTaggingSection?.includes("motilal-oswal-amc:nfo"),
  );
  const nonEtfFunds = nonNfoFunds.filter(
    (fund) => !fund?.fundsTaggingSection?.includes("motilal-oswal-amc:etf"),
  );
  const etfFunds = nonNfoFunds.filter(
    (fund) => fund?.fundsTaggingSection?.includes("motilal-oswal-amc:etf"),
  );
  return [...nfoFunds, ...nonEtfFunds, ...etfFunds];
};

function viewFunction(param) {

  const resolveSelectedPeriodKey = () => {
    const selectedPeriod = (
      dataMapMoObj.selectreturnstemp ||
      dataMapMoObj.deskrightdrp ||
      "3 years"
    )
      .toString()
      .trim();
    const mapped = dataMapMoObj.objtempdrop[selectedPeriod];
    if (mapped) {
      return dataMapMoObj.ObjTemp[mapped];
    }
    const fallbackKey = Object.keys(dataMapMoObj.objtempdrop).find(
      (k) => k.toLowerCase() === selectedPeriod.toLowerCase(),
    );
    return fallbackKey
      ? dataMapMoObj.ObjTemp[dataMapMoObj.objtempdrop[fallbackKey]]
      : dataMapMoObj.ObjTemp[dataMapMoObj.objtempdrop["3 years"]];
  };

  const getReturnByPlan = (fund, returnKey, targetPlanName) => {
    const planCode = fund?.planList?.find(
      (plan) => plan.planName === targetPlanName,
    )?.planCode;
    const returnObj = fund?.returns?.find((ret) => ret.plancode === planCode);
    const planVal = parseFloat(returnObj?.[returnKey]);
    if (!Number.isNaN(planVal) && planVal !== 0) {
      return planVal;
    }
    const fallbackVal = parseFloat(fund?.returns?.[0]?.[returnKey]);
    return Number.isNaN(fallbackVal) || fallbackVal === 0 ? null : fallbackVal;
  };

  let etfarry = [];
  let notetfarry = [];

  // Check current sort to see if we should preserve the user's sort order
  const sortText = param.querySelector(".sort-select-container .selectedtext")?.textContent?.trim() || "";
  const shouldPreserveSort = sortText === "Oldest to Newest" || sortText === "Newest to Oldest" || sortText === "By Returns";

  // Only reorganize if NOT using date/return sort
  if (!shouldPreserveSort) {
    dataMapMoObj.funddata.forEach((el) => {
      if (
        !el.fundsTaggingSection.includes("motilal-oswal-amc:nfo") &&
        el.fundsTaggingSection.includes("motilal-oswal-amc:etf")
      ) {
        etfarry.push(el);
      } else {
        notetfarry.push(el);
      }
    });

    etfarry.sort((a, b) => {
      const orderA = window.etfOrderMap.get(a.schemeName) ?? 9999;
      const orderB = window.etfOrderMap.get(b.schemeName) ?? 9999;

      return orderA - orderB;
    });

    const indexPositions = [];
    const indexItems = [];

    notetfarry.forEach((el, idx) => {
      if (
        !el.fundsTaggingSection.includes("motilal-oswal-amc:nfo") &&
        el.fundsTaggingSection.includes("motilal-oswal-amc:index-funds")
      ) {
        indexPositions.push(idx);
        indexItems.push(el);
      }
    });

    indexItems.sort((a, b) => {
      const orderA = window.indexOrderMap.get(a.schemeName) ?? 9999;
      const orderB = window.indexOrderMap.get(b.schemeName) ?? 9999;
      return orderA - orderB;
    });

    indexPositions.forEach((pos, i) => {
      notetfarry[pos] = indexItems[i];
    });
    // ✅ SORT within each group: Invest buttons first, then View INAV cards
    const sortByInvestStatus = (funds) => {
      return funds.sort((a, b) => {
        const statusA = getFundStatus(a);
        const statusB = getFundStatus(b);

        // investEnabled: true (Invest button) comes first (0)
        // investEnabled: false (View INAV) comes second (1)
        const investAFirst = statusA.investEnabled ? 0 : 1;
        const investBFirst = statusB.investEnabled ? 0 : 1;

        return investAFirst - investBFirst;
      });
    };

    // Sort non-ETF and ETF separately, then combine
    notetfarry = sortByInvestStatus(notetfarry);
    etfarry = sortByInvestStatus(etfarry);

    // ETF funds shown whenever the ETF checkbox is checked (alone or alongside others)
    const etfCheckbox = param.querySelector("#fundtype3");
    const etfChecked = etfCheckbox?.checked ?? false;
    dataMapMoObj.funddata = etfChecked
      ? [...notetfarry, ...etfarry]
      : [...notetfarry, ...etfarry]; // revert logic for FLP checkbox, show all funds
  }

  if (param.closest(".fund-listing-variant-two")) {
    const fundata = dataMapMoObj.funddata.filter((eldata) =>
      eldata.fundsTaggingSection.includes("motilal-oswal-amc:index-funds"),
    );
    dataMapMoObj.funddata = fundata;
  }

  // Keep funds with selected return period at the top, then show remaining funds.
  const selectedReturnKey = resolveSelectedPeriodKey();
  if (selectedReturnKey) {
    const targetPlanName = Array.from(
      param.querySelector(".togglebtn")?.classList || [],
    ).includes("toggle-checked")
      ? "Regular"
      : "Direct";
    const nfoFunds = [];
    const nonNfoFunds = [];
    dataMapMoObj.funddata.forEach((fund) => {
      if (fund?.fundsTaggingSection?.includes("motilal-oswal-amc:nfo")) {
        nfoFunds.push(fund);
      } else {
        nonNfoFunds.push(fund);
      }
    });
    // const hasSelectedPeriod = [];
    // const noSelectedPeriod = [];
    // nonNfoFunds.forEach((fund) => {
    //   const val = getReturnByPlan(fund, selectedReturnKey, targetPlanName);
    //   if (val === null) {
    //     noSelectedPeriod.push(fund);
    //   } else {
    //     hasSelectedPeriod.push(fund);
    //   }
    // });
    // dataMapMoObj.funddata = [
    //   ...nfoFunds,
    //   ...hasSelectedPeriod,
    //   ...noSelectedPeriod,
    // ];
  }

  dataMapMoObj.funddata = orderNonEtfFirst(dataMapMoObj.funddata);
  param.querySelector(".list-container").innerHTML = "";
  param.querySelector(".cards-container").innerHTML = "";
  if (
    Array.from(param.querySelector(".listby-container").classList).includes(
      "list-view-active",
    )
  ) {
    dataMapMoObj.funddata.forEach((el) => {
      param.querySelector(".list-container").append(listviewblock(el));
    });
    if (dataMapMoObj.deskrightdrp === "") {
      param.querySelector(".return-select-container p").textContent = "3 Years";
      dataMapMoObj.deskrightdrp = "3 Years";
    } else {
      param.querySelector(".return-select-container p").textContent =
        dataMapMoObj.deskrightdrp;
    }
  } else {
    dataMapMoObj.funddata.forEach((el) => {
      param.querySelector(".cards-container").append(fundcardblock(el));
    });
    if (dataMapMoObj.deskrightdrp === "") {
      param.querySelector(".return-select-container p").textContent = "3 Years";
      dataMapMoObj.deskrightdrp = "3 Years";
    } else {
      param.querySelector(".return-select-container p").textContent =
        dataMapMoObj.deskrightdrp;
    }
  }

  // dataMapMoObj.parseFunction(param, 'viewfunc');
}

function searchFunctionality(block) {
  // 1. Cache all necessary DOM element references
  const data = [];
  // 1. First, modify the tags for items that are no longer NFOs
  listingData.cfDataObjs.forEach((nfo) => {
    const funnfo = getFundStatus(nfo);
    if (
      !funnfo.isNFO &&
      nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
    ) {
      const indexval = nfo.fundsTaggingSection.indexOf("motilal-oswal-amc:nfo");
      nfo.fundsTaggingSection.splice(indexval, 1);
    }
  });

  // 2. Now, filter the main list to REMOVE non-investable NFOs
  // and assign the remaining NFOs to your variable.
  listingData.cfDataObjs = listingData.cfDataObjs.filter((nfo) => {
    const funnfo = getFundStatus(nfo);
    const hasNfoTag = nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo");

    // If it's an NFO but investment is disabled, return false to REMOVE it from cfDataObjs
    if (funnfo.isNFO && !funnfo.investEnabled) {
      return false;
    }

    // Keep everything else in cfDataObjs
    return true;
  });
  if (
    Array.from(block.querySelector(".cards-container").children).length !== 0
  ) {
    Array.from(block.querySelector(".cards-container").children).forEach(
      (cardel) => {
        data.push(cardel.querySelector(".star").getAttribute("schcode"));
      },
    );
    const tempDfilt = listingData.cfDataObjs.filter((el) => {
      if (!el.fundsTaggingSection || !el.planList) {
        return false;
      }
      return el;
    });
    dataMapMoObj.funddata = tempDfilt.filter((elobj) =>
      data.includes(elobj.schcode),
    );
  }
  if (
    Array.from(block.querySelector(".list-container").children).length !== 0
  ) {
    Array.from(block.querySelector(".list-container").children).forEach(
      (cardel) => {
        data.push(cardel.querySelector(".star").getAttribute("schcode"));
      },
    );
    const tempDfilt = listingData.cfDataObjs.filter((el) => {
      if (!el.fundsTaggingSection || !el.planList) {
        return false;
      }
      return el;
    });
    dataMapMoObj.funddata = tempDfilt.filter((elobj) =>
      data.includes(elobj.schcode),
    );
  }
  const searchContainer = document.querySelector(".search-input");
  const searchInput = searchContainer.querySelector(".search");
  const listContainer = searchContainer.querySelector(".list-search");
  // const listItems = searchContainer.querySelectorAll('.list-fund-name');
  const cancelButton = ensureCancelButton(
    searchContainer.querySelector(".cancel-search"),
  );
  const suggestionsStatus = searchContainer.querySelector(
    "#search-field-status",
  );

  const flpboolean = document.querySelector(".fund-toggle-wrap input").checked;
  const planflow = flpboolean ? "Regular" : "Direct";
  const mop = document.querySelector(".fund-toggle-wrap input");
  if (flpboolean) {
    mop.closest(".togglebtn").classList.add("toggle-checked");
  } else {
    mop.closest(".togglebtn").classList.remove("toggle-checked");
  }
  let datacd = [];
  const dataouter = [];
  const tempDfilt = listingData.cfDataObjs.filter((el) => {
    if (!el.fundsTaggingSection || !el.planList) {
      return false;
    }
    return el;
  });
  tempDfilt.forEach((elde, indexde) => {
    elde?.planList.forEach((elplan) => {
      // if (elplan.planName === planflow) {
      if (!datacd.includes(elplan.planName)) {
        datacd.push(elplan.planName);
      }
      // } //For Cache
    });
    if (datacd.length > 0) {
      dataouter.push({
        [indexde]: datacd,
        schemeName: elde.schemeName,
      });
      datacd = [];
    }
  });
  // console.log(dataouter);
  const FUND_DATA = dataouter.map((fund) => fund.schemeName);

  const getSchemeURL = (schemeName) => {
    const base = `${window.location.origin}/mutual-funds`;
    if (!schemeName) return `${base}/funds-details-page`;
    let slug = schemeName.split("/");
    slug = slug.at(-1);
    slug = slug.toLowerCase().replace(/\s+/g, '-');
    return `${base}/${slug}`;
  };

  const populateList = () => {
    listContainer.innerHTML = ""; // Clear list before populating
    FUND_DATA.forEach((fundName) => {
      const item = document.createElement("li");
      item.className = "list-fund-name";
      item.dataset.originalText = fundName;
      const link = document.createElement("a");
      link.href = getSchemeURL(fundName);
      link.textContent = fundName;
      item.appendChild(link);
      listContainer.appendChild(item);
    });
  };

  // --- SCRIPT INITIALIZATION ---
  populateList(); // Create the list on page load

  // --- IMPORTANT: Select listItems AFTER they have been created ---
  const listItems = searchContainer.querySelectorAll(".list-fund-name");
  listItems.forEach((item) => {
    item.dataset.originalText = item.textContent;
  });
  // --- End of Initialization ---

  const escapeRegExp = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  // The filter function remains the same
  // const filterListItems = (searchTerm) => {
  //   const term = searchTerm.trim();
  //   const existingNoResultsMessage = listContainer.querySelector('.no-results-message');
  //   if (existingNoResultsMessage) existingNoResultsMessage.remove();
  //   listContainer.classList.remove('no-search-list');

  //   if (!term) {
  //     listItems.forEach((item) => {
  //       item.innerHTML = item.dataset.originalText;
  //       item.style.display = 'list-item';
  //     });
  //     return;
  //   }

  //   const searchRegex = new RegExp(escapeRegExp(term), 'gi');
  //   let matchesFound = false;

  //   listItems.forEach((item) => {
  //     const {
  //       originalText,
  //     } = item.dataset;
  //     const match = originalText.match(searchRegex);
  //     if (match) {
  //       matchesFound = true;
  //       // const highlightedText =
  //       // originalText.replace(searchRegex, (mat) => `<strong>${mat}</strong>`);
  //       const highlightedText = originalText;
  //       item.innerHTML = highlightedText;
  //       item.style.display = 'list-item';
  //     } else {
  //       item.style.display = 'none';
  //     }
  //   });

  //   if (!matchesFound) {
  //     listContainer.classList.add('no-search-list');
  //     const messageItem = document.createElement('li');
  //     messageItem.className = 'list-fund-name no-results-message';
  //     messageItem.textContent = 'No matching results';
  //     listContainer.appendChild(messageItem);
  //   }
  // };

  const updateSuggestionStatus = (searchTerm) => {
    if (!suggestionsStatus) return;
    const term = searchTerm.trim();
    if (!term) {
      suggestionsStatus.textContent = "";
      return;
    }
    const visibleSuggestions = Array.from(
      listContainer.querySelectorAll(
        ".list-fund-name:not(.no-results-message)",
      ),
    ).filter((item) => item.style.display !== "none");
    const count = visibleSuggestions.length;
    suggestionsStatus.textContent = `${count} suggestion${count === 1 ? "" : "s"} available.`;
  };

  const filterListItems = (searchTerm) => {
    const term = searchTerm.trim();
    const existingNoResultsMessage = listContainer.querySelector(
      ".no-results-message",
    );

    if (existingNoResultsMessage) existingNoResultsMessage.remove();
    listContainer.classList.remove("no-search-list");

    // if (!term) {
    //   listItems.forEach((item) => {
    //     const link = item.querySelector('a');
    //     if (link) link.textContent = item.dataset.originalText;
    //     item.style.display = 'list-item';
    //   });
    //   return;
    // }

    if (!term) {
      listItems.forEach((item) => {
        const link = item.querySelector("a") || document.createElement("a");
        link.textContent = item.dataset.originalText;
        link.href = getSchemeURL(item.dataset.originalText);
        if (!link.parentElement) item.appendChild(link);
        item.style.display = "list-item";
      });
      updateSuggestionStatus("");
      return;
    }

    const searchRegex = new RegExp(escapeRegExp(term), "gi");
    let matchesFound = false;

    listItems.forEach((item) => {
      const { originalText } = item.dataset;
      const match = originalText.match(searchRegex);
      if (match) {
        matchesFound = true;
        // const highlightedText =
        // originalText.replace(searchRegex, (mat) => `<strong>${mat}</strong>`);

        // Highlight searched text
        const highlightedText = originalText.replace(
          searchRegex,
          (match) => `<span class="search-highlight">${match}</span>`,
        );
        const link = item.querySelector("a") || document.createElement("a");
        link.innerHTML = highlightedText;
        link.href = getSchemeURL(originalText);
        if (!link.parentElement) item.appendChild(link);
        item.style.display = "list-item";
        // const highlightedText = originalText;
        // const link = item.querySelector('a');
        // if (link) link.textContent = highlightedText;
        // item.style.display = 'list-item';
      } else {
        item.style.display = "none";
      }
    });

    if (!matchesFound) {
      listContainer.classList.add("no-search-list");

      const messageItem = document.createElement("li");
      messageItem.className = "list-fund-name no-results-message";
      messageItem.textContent = "No matching results";

      listContainer.appendChild(messageItem);
    }

    updateSuggestionStatus(term);
  };

  searchInput.addEventListener("focus", () => {
    searchContainer.classList.add("search-active");
    if (window.visualViewport) {
      // This event fires whenever the viewport is resized or zoomed
      window.visualViewport.addEventListener("resize", () => {
        window.visualViewport.scale = 1;
      });
    }
  });

  searchContainer.addEventListener("focusout", () => {
    requestAnimationFrame(() => {
      if (!searchContainer.contains(document.activeElement)) {
        searchContainer.classList.remove("search-active");

        currentFocusIndex = -1;

        const visibleItems = Array.from(
          listContainer.querySelectorAll(".list-fund-name"),
        );

        updateActiveItem(visibleItems);

        cancelButton.style.display =
          searchInput.value.length > 0 ? "flex" : "none";
      }
    });
  });

  searchContainer.classList.remove("search-active");
  searchInput.addEventListener("input", (event) => {
    searchContainer.classList.add("search-active");
    filterListItems(event.target.value);
    cancelButton.style.display =
      event.target.value.length > 0 ? "flex" : "none";
  });

  let currentFocusIndex = -1;

  function updateActiveItem(items) {
    items.forEach((item, idx) => {
      if (idx === currentFocusIndex) {
        item.classList.add("active-search-item");
        item.scrollIntoView({
          block: "nearest",
        });
      } else {
        item.classList.remove("active-search-item");
      }
    });
  }
  searchInput.addEventListener("keydown", (event) => {
    const visibleItems = Array.from(
      listContainer.querySelectorAll(".list-fund-name"),
    ).filter(
      (item) =>
        item.style.display !== "none" &&
        !item.classList.contains("no-results-message"),
    );

    if (event.key === "Escape") {
      event.preventDefault();
      currentFocusIndex = -1;
      searchContainer.classList.remove("search-active");
      searchInput.focus();
      return false;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      currentFocusIndex = (currentFocusIndex + 1) % visibleItems.length;
      updateActiveItem(visibleItems);
      // return false;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      currentFocusIndex =
        (currentFocusIndex - 1 + visibleItems.length) % visibleItems.length;
      updateActiveItem(visibleItems);
      // return false;
    }
    if (event.key === "Enter") {
      if (visibleItems[currentFocusIndex]) {
        // visibleItems[currentFocusIndex].click();
        searchInput.value = visibleItems[currentFocusIndex].textContent;
      } else if (visibleItems.length > 0) {
        // visibleItems[0].click();
        searchInput.value = visibleItems[0].textContent;
      }
      searchContainer.classList.remove("search-active");
      const tempDfilta = listingData.cfDataObjs.filter((el) => {
        if (!el.fundsTaggingSection || !el.planList) {
          return false;
        }
        return el;
        6;
      });
      dataMapMoObj.funddata = tempDfilta.filter(
        (ellim) => ellim.schemeName === searchInput.value,
      );
      // viewFunction(block);
      // CARD HIDE LOGIC ON SEARCH
      const cardsContainercd = block.querySelector(".filter-cards");
      const cardsContainer = cardsContainercd.querySelector(".cards-container");
      const squarecard = block.querySelector(".squareby-container");
      if (Array.from(squarecard.classList).includes("grid-view-active")) {
        const tempDfiltone = listingData.cfDataObjs.filter((el) => {
          if (!el.fundsTaggingSection || !el.planList || !el.returns) {
            return false;
          }
          return el;
        });
        const datatem = tempDfiltone.filter(
          (elsch) => elsch.schemeName === searchInput.value,
        );
        if (datatem[0] !== undefined) {
          cardsContainer.innerHTML = "";
          cardsContainer.append(fundcardblock(datatem[0]));
        }
      }

      const listHeadercd = block.querySelector(".filter-cards");
      const listHeader = listHeadercd.querySelector(".list-container");
      const listcard = block.querySelector(".listby-container");
      if (Array.from(listcard).includes("list-view-active")) {
        if (cardsContainer && cardsContainer.checkVisibility()) {
          const tempDfilttwo = listingData.cfDataObjs.filter((el) => {
            if (!el.fundsTaggingSection || !el.planList || !el.returns) {
              return false;
            }
            return el;
          });
          const datatem = tempDfilttwo.filter(
            (elsch) => elsch.schemeName === searchInput.value,
          );
          if (datatem[0] !== undefined) {
            listHeader.innerHTML = "";
            listHeader.append(listviewblock(datatem[0]));
          }
        }
      }
      cancelButton.style.display =
        searchInput.value.length > 0 ? "flex" : "none";
      const flitwrap = block.querySelector(".applied-filter-wrap");
      if (Array.from(flitwrap.classList).includes("filter-active")) {
        flitwrap.classList.remove("filter-active");
      }
      Array.from(block.querySelector(".filter-list-wrapper").children).forEach(
        (el) => {
          if (
            el.closest(".checkbox-label-container") !== null &&
            el
              .closest(".checkbox-label-container")
              ?.querySelector(".innerindianequity")
          ) {
            el.closest(".checkbox-label-container")
              .querySelectorAll(".innerindianequity input")
              .forEach((elemsub) => {
                if (elemsub.checked) {
                  elemsub.checked = false;
                }
              });
          }
          if (
            el.closest(".checkbox-label-container") !== null &&
            el.querySelector("input").checked
          ) {
            // const moplabel = el.querySelector('input').nextElementSibling;
            if (
              !Array.from(el.querySelector("input").classList).includes(
                "indian-equity",
              )
            ) {
              if (el.querySelector("input").checked) {
                el.querySelector("input").checked = false;
              }
            }
          }
        },
      );
      return false;
    }
    if (event.key === "Backspace" || event.key === "Delete") {
      currentFocusIndex = -1; // Reset selection on backspace/delete
      const cardsContainer = block.querySelector(
        ".filter-cards .cards-container",
      );

      if (cardsContainer && cardsContainer.checkVisibility()) {
        const popular = listingData.mostBoughtFunds.map(
          (el) => el.split(":")[0],
        );
        const tempDfiltthree = listingData.cfDataObjs.filter((el) => {
          if (!popular.includes(el.schemeName)) {
            return false;
          }
          return el;
        });
        const datatem = tempDfiltthree.slice(0, 10);
        if (datatem[0] !== undefined) {
          cardsContainer.innerHTML = "";
          datatem.forEach((elcard) =>
            cardsContainer.append(fundcardblock(elcard)),
          );
        }
      }
      const listHeader = block.querySelector(".filter-cards .list-container");
      if (listHeader && listHeader.checkVisibility()) {
        if (cardsContainer && cardsContainer.checkVisibility()) {
          const popular = listingData.mostBoughtFunds.map(
            (el) => el.split(":")[0],
          );
          const tempDfiltfour = listingData.cfDataObjs.filter((el) => {
            if (!popular.includes(el.schemeName)) {
              return false;
            }
            return el;
          });
          const datatem = tempDfiltfour.slice(0, 10);
          if (datatem[0] !== undefined) {
            listHeader.innerHTML = "";
            datatem.forEach((elist) =>
              cardsContainer.append(listviewblock(elist)),
            );
          }
        }
      }
      return false;
    }
    return event;
  });

  listContainer.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    link.removeAttribute("href");
    const item = event.target.closest(
      ".list-fund-name:not(.no-results-message)",
    );
    if (item) {
      searchInput.value = item.dataset.originalText || item.textContent.trim();
      searchContainer.classList.remove("search-active");
      const tempDfiltfive = listingData.cfDataObjs.filter((el) => {
        if (!el.fundsTaggingSection || !el.planList) {
          return false;
        }
        return el;
      });
      dataMapMoObj.funddata = tempDfiltfive.filter(
        (ellim) => ellim.schemeName === searchInput.value,
      );
      viewFunction(block);
      // CARD HIDE LOGIC ON SEARCH
      const cardsContainercd = block.querySelector(".filter-cards");
      const cardsContainer = cardsContainercd.querySelector(".cards-container");
      const squarecard = block.querySelector(".squareby-container");
      if (Array.from(squarecard.classList).includes("grid-view-active")) {
        const tempDfiltsix = listingData.cfDataObjs.filter((el) => {
          if (!el.fundsTaggingSection || !el.planList || !el.returns) {
            return false;
          }
          return el;
        });
        const datatem = tempDfiltsix.filter(
          (elsch) => elsch.schemeName === searchInput.value,
        );
        if (datatem[0] !== undefined) {
          cardsContainer.innerHTML = "";
          cardsContainer.append(fundcardblock(datatem[0]));
        }
      }

      const listHeadercd = block.querySelector(".filter-cards");
      const listHeader = listHeadercd.querySelector(".list-container");
      const listcard = block.querySelector(".listby-container");
      if (Array.from(listcard).includes("list-view-active")) {
        if (cardsContainer && cardsContainer.checkVisibility()) {
          const tempDfilta = listingData.cfDataObjs.filter((el) => {
            if (!el.fundsTaggingSection) {
              return false;
            }
            return el;
          });
          const datatem = tempDfilta.filter(
            (elsch) => elsch.schemeName === searchInput.value,
          );
          if (datatem[0] !== undefined) {
            listHeader.innerHTML = "";
            listHeader.append(listviewblock(datatem[0]));
          }
        }
      }
      cancelButton.style.display =
        searchInput.value.length > 0 ? "flex" : "none";
      const flitwrap = block.querySelector(".applied-filter-wrap");
      if (Array.from(flitwrap.classList).includes("filter-active")) {
        flitwrap.classList.remove("filter-active");
      }
      Array.from(block.querySelector(".filter-list-wrapper").children).forEach(
        (el) => {
          if (
            el.closest(".checkbox-label-container") !== null &&
            el
              .closest(".checkbox-label-container")
              ?.querySelector(".innerindianequity")
          ) {
            el.closest(".checkbox-label-container")
              .querySelectorAll(".innerindianequity input")
              .forEach((elemsub) => {
                if (elemsub.checked) {
                  elemsub.checked = false;
                }
              });
          }
          if (el.querySelector("input").checked) {
            // const moplabel = el.querySelector('input').nextElementSibling;
            if (
              !Array.from(el.querySelector("input").classList).includes(
                "indian-equity",
              )
            ) {
              if (el.querySelector("input").checked) {
                el.querySelector("input").checked = false;
              }
            }
          }
        },
      );
      if (link) {
        event.preventDefault();
        return false;
        window.location.href = link.href;
      }
      return event;
    }
  });

  cancelButton.addEventListener("click", () => {
    searchInput.value = "";
    filterListItems("");
    cancelButton.style.display = "none";
    searchContainer.classList.remove("search-active");
    if (suggestionsStatus) suggestionsStatus.textContent = "";
    const popular = listingData.mostBoughtFunds.map((el) => el.split(":")[0]);
    const tempDfiltseven = listingData.cfDataObjs.filter((el) => {
      if (!popular.includes(el.schemeName)) {
        return false;
      }
      return el;
    });
    dataMapMoObj.funddata = tempDfiltseven.slice(0, 10);
    viewFunction(block);
  });

  document.addEventListener("click", (event) => {
    try {
      if (!searchContainer.contains(event.target)) {
        searchContainer.classList.remove("search-active");
        // searchInput.value = ""
      }
      document
        .querySelectorAll(".cagr-container .cagr-select-wrapper")
        .forEach((el) => {
          if (!el.contains(event.target)) {
            el.querySelector(".dropdown-list").classList.remove(
              "dropdown-active",
            );
          }
        });
      // document.querySelectorAll('.card-category').forEach((el) => {
      //   if (!el.contains(event.target)) {
      //     el.querySelector('.dropdown-list').classList.remove('dropdown-active');
      //   }
      // });
    } catch (error) {
      // console.log(error);
    }
  });

  if (searchInput.value.length === 0) {
    cancelButton.style.display = "none";
  }
  return false;
}

function checkfilter(block) {
  const searInp = block.querySelector(".search-input input");
  searInp.value = "";
  const cancelBtn = ensureCancelButton(block.querySelector(".cancel-search"));
  cancelBtn.style.display = "none";
  const filterTag = []; // 5-8-25
  let tempData = [];
  // if ((block.querySelector('#fundtype1').checked
  //   || block.querySelector('#fundtype2').checked
  //   || block.querySelector('#fundtype3').checked)
  //   && block.querySelectorAll('.filter-list-wrapper [type="checkbox"]:checked').length > 1) {
  //   Array.from(block.querySelector('.filter-list-wrapper').children).forEach((el) => {
  //     if (el.closest('.checkbox-label-container') !== null && el.closest('.checkbox-label-container')?.querySelector('.innerindianequity')) {
  //       el.closest('.checkbox-label-container').querySelectorAll('.innerindianequity input').forEach((elemsub) => {
  //         if (elemsub.checked && !tempData.includes(elemsub.getAttribute('dataattr'))) {
  //           filterTag.push(elemsub.nextElementSibling.textContent.trim().split('(')[0]); // 5-8-25
  //           tempData.push(elemsub.getAttribute('dataattr'));
  //         }
  //       });
  //     }
  //     if (el.closest('.checkbox-label-container') !== null && el.querySelector('input').checked) {
  //       const moplabel = el.querySelector('input').nextElementSibling;
  //       const finlabel = moplabel.querySelector('label').textContent.split('(')[0];
  //       filterTag.push(finlabel); // 5-8-25
  //       if (!Array.from(el.querySelector('input').classList).includes('indian-equity')) {
  //         tempData.push(el.querySelector('input').getAttribute('dataattr'));
  //       }
  //     }
  //   });
  //   const allCodes = tempData.flatMap((str) => str.split('-')).filter((c) => c);
  //   const duplicates = allCodes.filter((code, index) => allCodes.indexOf(code) !== index);
  //   const commonCodesAcrossGroups = [...new Set(duplicates)];
  //   tempData = commonCodesAcrossGroups;
  // } else {
  Array.from(block.querySelector(".filter-list-wrapper").children).forEach(
    (el) => {
      if (
        el.closest(".checkbox-label-container") !== null &&
        el
          .closest(".checkbox-label-container")
          ?.querySelector(".innerindianequity")
      ) {
        el.closest(".checkbox-label-container")
          .querySelectorAll(".innerindianequity input")
          .forEach((elemsub) => {
            if (
              elemsub.checked &&
              window.getComputedStyle(
                elemsub.closest(".checkbox-label-container") || elemsub,
              ).display !== "none" &&
              !tempData.includes(elemsub.getAttribute("dataattr"))
            ) {
              filterTag.push(
                elemsub.nextElementSibling.textContent.trim().split("(")[0],
              ); // 5-8-25
              elemsub
                .getAttribute("dataattr")
                .split("-")
                .forEach((eldata) => {
                  if (!tempData.includes(eldata)) {
                    tempData.push(eldata);
                  }
                });
            }
          });
      }
      if (
        el.closest(".checkbox-label-container") !== null &&
        el.querySelector("input").checked &&
        window.getComputedStyle(el.closest(".checkbox-label-container"))
          .display !== "none"
      ) {
        const moplabel = el.querySelector("input").nextElementSibling;
        const finlabel = moplabel
          .querySelector("label")
          .textContent.split("(")[0];
        filterTag.push(finlabel); // 5-8-25
        if (
          !Array.from(el.querySelector("input").classList).includes(
            "indian-equity",
          )
        ) {
          el.querySelector("input")
            .getAttribute("dataattr")
            .split("-")
            .forEach((eldata) => {
              if (!tempData.includes(eldata)) {
                tempData.push(eldata);
              }
            });
        }
      }
    },
  );
  // }
  dataMapMoObj.funddata = [];
  const tempDfilt = listingData.cfDataObjs.filter((el) => {
    if (!el.fundsTaggingSection || !el.planList) {
      return false;
    }
    return el;
  });
  dataMapMoObj.funddata =
    tempData.length > 0
      ? tempDfilt.filter((el) => tempData.includes(el.schcode))
      : [];
  const sorttextcont = block.querySelector(
    ".sort-select-container .selectedtext",
  );
  const sorttext = sorttextcont.textContent.trim();
  if (dataMapMoObj.funddata.length === 0 && filterTag.length === 0) {
    if (sorttext === "Popular") {
      dataMapMoObj.funddata = "";
      const popular = listingData.mostBoughtFunds.map((el) => el.split(":")[0]);

      // const nfofund = listingData.cfDataObjs.filter((nfo) => {
      //   const funnfo = getFundStatus(nfo);
      //   if (!funnfo.isNFO && nfo.fundsTaggingSection.includes('motilal-oswal-amc:nfo')) {
      //     const indexval = nfo.fundsTaggingSection.indexOf('motilal-oswal-amc:nfo');
      //     nfo.fundsTaggingSection.splice(indexval, 1);
      //   }
      //   if (funnfo.isNFO && !funnfo.investEnabled &&
      // nfo.fundsTaggingSection.includes('motilal-oswal-amc:nfo')) {
      //     listingData.cfDataObjs = listingData.cfDataObjs.
      // filter((el, indexval) => listingData.cfDataObjs.indexOf(nfo) !== indexval)
      //   }
      //   return funnfo.isNFO && nfo.fundsTaggingSection.includes('motilal-oswal-amc:nfo');
      // });
      // if (nfofund.length !== 0) {
      //   const fundstatusv3 = getFundStatus(nfofund[0]);
      //   if (nfofund.length !== 0 && !fundstatusv3.isNFO && [...nfofund[0].fundsTaggingSection].includes('motilal-oswal-amc:nfo')) {
      //     const tags = nfofund[0].fundsTaggingSection.filter((item) => item !== 'motilal-oswal-amc:nfo');
      //     nfofund[0].fundsTaggingSection = tags || [];
      //   }
      // }

      // 1. First, modify the tags for items that are no longer NFOs
      listingData.cfDataObjs.forEach((nfo) => {
        const funnfo = getFundStatus(nfo);
        if (
          !funnfo.isNFO &&
          nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        ) {
          const indexval = nfo.fundsTaggingSection.indexOf(
            "motilal-oswal-amc:nfo",
          );
          nfo.fundsTaggingSection.splice(indexval, 1);
        }
      });

      // 2. Now, filter the main list to REMOVE non-investable NFOs
      // and assign the remaining NFOs to your variable.
      listingData.cfDataObjs = listingData.cfDataObjs.filter((nfo) => {
        const funnfo = getFundStatus(nfo);
        const hasNfoTag = nfo.fundsTaggingSection.includes(
          "motilal-oswal-amc:nfo",
        );

        // If it's an NFO but investment is disabled, return false to REMOVE it from cfDataObjs
        if (funnfo.isNFO && !funnfo.investEnabled) {
          return false;
        }

        // Keep everything else in cfDataObjs
        return true;
      });

      // 3. Finally, get your specific subset of NFO funds from the cleaned list
      const nfofund = listingData.cfDataObjs.filter((nfo) => {
        const funnfo = getFundStatus(nfo);
        return (
          funnfo.isNFO &&
          nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        );
      });

      let tempDfilteight = listingData.cfDataObjs.filter((el) => {
        if (!popular.includes(el.schemeName)) {
          return false;
        }
        return el;
      });
      if (nfofund.length !== 0) {
        tempDfilteight = appendUniqueFunds(tempDfilteight, nfofund);
      }
      dataMapMoObj.funddata = tempDfilteight;
    }
    if (dataMapMoObj.funddata.length === 0) {
      dataMapMoObj.funddata = listingData.cfDataObjs;
    }
    if (sorttext === "Oldest to Newest") {
      const tempDfiltnine = dataMapMoObj.funddata.filter((el) => {
        if (!el.fundsTaggingSection || !el.planList) {
          return false;
        }
        return el;
      });
      const tempDataad = JSON.parse(JSON.stringify(tempDfiltnine));
      const tempa = tempDataad.sort(
        (a, b) => new Date(a.dateOfAllotment) - new Date(b.dateOfAllotment),
      );
      dataMapMoObj.funddata = "";
      dataMapMoObj.funddata = tempa;
    }
    if (sorttext === "Newest to Oldest") {
      const tempDfilteleven = dataMapMoObj.funddata.filter((el) => {
        if (!el.fundsTaggingSection || !el.planList) {
          return false;
        }
        return el;
      });
      const tempDataad = JSON.parse(JSON.stringify(tempDfilteleven));
      const tempa = tempDataad.sort(
        (a, b) => new Date(b.dateOfAllotment) - new Date(a.dateOfAllotment),
      );
      dataMapMoObj.funddata = "";
      dataMapMoObj.funddata = tempa;
    }
    if (sorttext === "By Returns") {
      const selectedPeriod = dataMapMoObj.selectreturnstemp || "3 years";
      const selectdrop =
        dataMapMoObj.ObjTemp[dataMapMoObj.objtempdrop[selectedPeriod]];
      const targetPlanName = Array.from(
        block.querySelector(".togglebtn").classList,
      ).includes("toggle-checked")
        ? "Regular"
        : "Direct";

      let tempDfiltninteen = dataMapMoObj.funddata
        .filter((fund) => fund?.planList?.length)
        .sort((alist, blist) => {
          return (
            getBestAvailableReturn(blist, targetPlanName, selectdrop) -
            getBestAvailableReturn(alist, targetPlanName, selectdrop)
          );
        });

      // The fund with the highest return is now at index 0
      // console.log(tempDfiltninteen);
      const nfofund = listingData.cfDataObjs.filter((nfo) => {
        const funnfo = getFundStatus(nfo);
        if (
          !funnfo.isNFO &&
          nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        ) {
          const indexval = nfo.fundsTaggingSection.indexOf(
            "motilal-oswal-amc:nfo",
          );
          nfo.fundsTaggingSection.splice(indexval, 1);
        }
        if (
          funnfo.isNFO &&
          !funnfo.investEnabled &&
          nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        ) {
          listingData.cfDataObjs = listingData.cfDataObjs.filter(
            (el, indexval) => listingData.cfDataObjs.indexOf(nfo) !== indexval,
          );
        }
        return (
          funnfo.isNFO &&
          nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        );
      });
      if (nfofund.length !== 0) {
        const fundstatus = getFundStatus(nfofund[0]);
        if (
          nfofund.length !== 0 &&
          !fundstatus.isNFO &&
          [...nfofund[0].fundsTaggingSection].includes("motilal-oswal-amc:nfo")
        ) {
          const tags = nfofund[0].fundsTaggingSection.filter(
            (item) => item !== "motilal-oswal-amc:nfo",
          );
          nfofund[0].fundsTaggingSection = tags || [];
        }
        dataMapMoObj.funddata = dataMapMoObj.funddata.filter((filterel) => {
          const tags = filterel.fundsTaggingSection;
          if (!tags) return true; // Keep the item if there are no tags to check
          return filterel.schcode !== nfofund[0].schcode;
        });
      }
      if (tempDfiltninteen.length === 0) {
        // if (shouldShowCard(nfofund)) {
        tempDfiltninteen = listingData.cfDataObjs;
        // .slice(1, 11);
        // }
      }
      if (nfofund.length !== 0) {
        tempDfiltninteen = appendUniqueFunds(tempDfiltninteen, nfofund);
      }
      const tempa = JSON.parse(JSON.stringify(tempDfiltninteen));
      dataMapMoObj.funddata = "";
      dataMapMoObj.funddata = tempa;
    }
  }

  viewFunction(block);

  if (sorttext === "By Returns") {
    const selectedPeriod = dataMapMoObj.selectreturnstemp || "3 years";
    const selectdrop =
      dataMapMoObj.ObjTemp[dataMapMoObj.objtempdrop[selectedPeriod]];
    const targetPlanName = Array.from(
      block.querySelector(".togglebtn").classList,
    ).includes("toggle-checked")
      ? "Regular"
      : "Direct";

    let tempDfiltninteena = dataMapMoObj.funddata
      .filter((fund) => fund?.planList?.length)
      .sort((alist, blist) => {
        return (
          getBestAvailableReturn(blist, targetPlanName, selectdrop) -
          getBestAvailableReturn(alist, targetPlanName, selectdrop)
        );
      });
    const nfofund = dataMapMoObj.funddata.filter((nfo) => {
      const funnfo = getFundStatus(nfo);
      return (
        funnfo.isNFO &&
        funnfo.investEnabled &&
        nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
      );
    });
    if (nfofund.length !== 0) {
      const fundstatus = getFundStatus(nfofund[0]);
      if (
        nfofund.length !== 0 &&
        !fundstatus.isNFO &&
        [...nfofund[0].fundsTaggingSection].includes("motilal-oswal-amc:nfo")
      ) {
        const tags = nfofund[0].fundsTaggingSection.filter(
          (item) => item !== "motilal-oswal-amc:nfo",
        );
        nfofund[0].fundsTaggingSection = tags || [];
      }
      dataMapMoObj.funddata = dataMapMoObj.funddata.filter(
        (filterel) => filterel.schcode !== nfofund[0].schcode,
      );
    }
    if (nfofund.length !== 0) {
      // if (shouldShowCard(nfofund)) {
      tempDfiltninteena = appendUniqueFunds(tempDfiltninteena, nfofund);
      // }
    }
    const tempa = JSON.parse(JSON.stringify(tempDfiltninteena));
    dataMapMoObj.funddata = "";
    dataMapMoObj.funddata = tempa;
    viewFunction(block);
  }

  function filterGroup(Filterparam) {
    const appliedList = block.querySelector(".applied-filter-list");
    appliedList.innerHTML = "";

    // Render applied filters
    for (let i = 0; i < Filterparam.length; i += 1) {
      const dspclose = Filterparam[i] === "Indian Equity" ? "none" : "flex";
      appliedList.innerHTML += `<li class="applied-filter-name" style="display:${dspclose}"><span>${Filterparam[i]}</span><button type="button" class="remove-filter-btn" aria-label="Remove ${Filterparam[i]} filter"><img src="/icons/cross-icon.svg" alt="" class="filter-cross-icon" aria-hidden="true"/></button></li>`;
    }
    if (Filterparam.length !== 0) {
      if (Filterparam.length === 1 && Filterparam[0] === "Indian Equity") {
        document.querySelector(".filter-list-wrapper .indian-equity").checked =
          false;
        appliedList
          .closest(".applied-filter-wrap")
          .classList.remove("filter-active");
        return false;
      }
      appliedList
        .closest(".applied-filter-wrap")
        .classList.add("filter-active");
    } else {
      appliedList
        .closest(".applied-filter-wrap")
        .classList.remove("filter-active");
      return false;
    }
    // Add remove logic for each tag
    const appliedItems = Array.from(appliedList.children);
    for (let i = 0; i < appliedItems.length; i += 1) {
      const removeBtn = appliedItems[i].querySelector(".remove-filter-btn");
      if (!removeBtn) continue;
      removeBtn.addEventListener("click", (event) => {
        const updatedFilterTag = [];
        const clickedText = event.target
          .closest(".applied-filter-name")
          .querySelector("span").textContent;

        const currentItems = Array.from(appliedList.children);
        for (let j = 0; j < currentItems.length; j += 1) {
          const spanText = currentItems[j].querySelector("span").textContent;
          if (spanText !== clickedText) {
            updatedFilterTag.push(spanText);
          }
        }

        // Re-render after removal
        filterGroup(updatedFilterTag);

        // Uncheck logic
        const filterItems = Array.from(
          block.querySelector(".filter-list-wrapper").children,
        );
        for (let k = 0; k < filterItems.length; k += 1) {
          const item = filterItems[k];
          const checkboxContainer = item.closest(".checkbox-label-container");
          if (checkboxContainer) {
            const innerEquity =
              checkboxContainer.querySelector(".innerindianequity");
            if (innerEquity) {
              const subInputs = innerEquity.querySelectorAll("input");
              for (let l = 0; l < subInputs.length; l += 1) {
                const innerFundFilter = subInputs[
                  l
                ].nextElementSibling.textContent
                  .trim()
                  .split("(")[0];
                if (updatedFilterTag.indexOf(innerFundFilter) === -1) {
                  subInputs[l].checked = false;
                  const labelnum = subInputs[l].nextElementSibling;
                  if (labelnum.querySelector(".tempcount") !== null) {
                    labelnum.querySelector(".tempcount").textContent = "";
                  }
                  if (updatedFilterTag.length === 0) {
                    appliedList
                      .closest(".applied-filter-wrap")
                      .classList.remove("filter-active");
                  }
                }
              }
            }

            const inp = item.querySelector("input");
            if (inp) {
              const idAttr = inp.getAttribute("id");
              const outerLabel = checkboxContainer
                .querySelector("label")
                ?.textContent.replace(/\d+/g, "")
                .replaceAll("()", "")
                .trim();

              if (
                idAttr.includes("index") &&
                outerLabel &&
                updatedFilterTag.indexOf(outerLabel) === -1
              ) {
                inp.checked = false;
              } else if (
                idAttr.includes("fundtype") &&
                outerLabel &&
                updatedFilterTag.indexOf(outerLabel) === -1
              ) {
                inp.checked = false;
              } else if (
                updatedFilterTag.length === 1 &&
                updatedFilterTag[0] === "Indian Equity"
              ) {
                appliedList
                  .closest(".applied-filter-wrap")
                  .classList.remove("filter-active");
                inp.checked = false;
              }

              checkfilter(block);
            }
          }
        }
      });
    }

    return block;
  }

  return filterGroup(filterTag);
}

function applyFunction(block, options = {}) {
  const { forceMobileApply = false } = options;

  let temp =
    dataMapMoObj.tempMobReturn === undefined ? [] : dataMapMoObj.tempMobReturn;
  const tempDfilt = listingData.cfDataObjs.filter((el) => {
    if (!el.fundsTaggingSection || !el.planList) {
      return false;
    }
    return el;
  });
  temp =
    dataMapMoObj.tempMobReturn.length !== 0 ? temp : tempDfilt;
  dataMapMoObj.tempMobReturn = temp;
  const isFilterOverlayActive = Array.from(
    block.querySelector(".filter-overlay").classList,
  ).includes("active");
  const isSortOverlayActive = Array.from(
    block.querySelector(".sort-overlay").classList,
  ).includes("active");
  const shouldApplyOnMobileLoad = forceMobileApply && window.innerWidth < 786;

  if (isFilterOverlayActive || shouldApplyOnMobileLoad) {
    dataMapMoObj.funddata = dataMapMoObj.tempMobReturn;
    dataMapMoObj.tempMobReturn = [];
    if (isFilterOverlayActive) {
      block.querySelector(".filter-overlay").classList.remove("active");
    }
    checkfilter(block);
  } else if (isSortOverlayActive) {
    dataMapMoObj.funddata = dataMapMoObj.tempMobReturn;
    dataMapMoObj.tempMobReturn = [];
    if (dataMapMoObj.flagsort === "Y") {
      dataMapMoObj.flagsort = "";
      const flitwrap = block.querySelector(".applied-filter-wrap");
      if (Array.from(flitwrap.classList).includes("filter-active")) {
        flitwrap.classList.remove("filter-active");
      }
      Array.from(block.querySelector(".filter-list-wrapper").children).forEach(
        (el) => {
          if (
            el.closest(".checkbox-label-container") !== null &&
            el
              .closest(".checkbox-label-container")
              ?.querySelector(".innerindianequity")
          ) {
            el.closest(".checkbox-label-container")
              .querySelectorAll(".innerindianequity input")
              .forEach((elemsub) => {
                if (elemsub.checked) {
                  elemsub.checked = false;
                }
              });
          }
          if (
            el.closest(".checkbox-label-container") !== null &&
            el.querySelector("input").checked
          ) {
            // const moplabel = el.querySelector('input').nextElementSibling;
            if (
              !Array.from(el.querySelector("input").classList).includes(
                "indian-equity",
              )
            ) {
              if (el.querySelector("input").checked) {
                el.querySelector("input").checked = false;
              }
            } else {
              el.querySelector("input").checked = false;
            }
          }
        },
      );
    }
    block.querySelector(".sort-overlay").classList.remove("active");
    dataMapMoObj.selectreturns =
      dataMapMoObj.objtempdrop[dataMapMoObj.selectreturnstemp];
    block.querySelector(".sort-select-container .selectedtext").textContent =
      "";
    block.querySelector(".sort-select-container .selectedtext").textContent =
      dataMapMoObj.schmenmob;
    block.querySelector(".return-select-container .selectedtext").textContent =
      "";
    block.querySelector(".return-select-container .selectedtext").textContent =
      dataMapMoObj.selectreturns;

    const searInp = block.querySelector(".search-input input");
    searInp.value = "";
    const cancelBtn = ensureCancelButton(block.querySelector(".cancel-search"));
    cancelBtn.style.display = "none";

    viewFunction(block);
  }
  block.closest("body").classList.remove("scroll-lock");
  if (window.innerWidth < 786) {
    block.scrollIntoView({
      behavior: "smooth",
    });
  }
}

dataMapMoObj.parseFunction = (param, attrparam) => {
  if (attrparam === "viewfunc") {
    searchFunctionality(param);
  }
};

const smallcase = [
  "sid",
  "etf",
  "nav",
  "sip",
  "kim",
  "ssd",
  "pms",
  "aif",
  "iap",
  "sai",
  "kyc",
  "nri",
  "otm",
  "moamc",
  "amc",
  "bop",
  "gdp",
  "elss",
  "nfo",
  "ecs",
  "bse",
  "nsc",
  "ntdop",
  "iop",
  "Fms",
];

export default async function decorate(block) {

  if (window.location.pathname.includes("/mutual-funds")) {
    const faqmf = document.querySelector('.freq-ask-ques');
    faqmf?.classList?.add('faq-campaign');
  }

  // Add to Cart Structure
  if (block.closest(".section").getAttribute("data-id") === "add-to-cart") {
    const { default: addToCart } = await import(
      "./add-to-cart/add-to-cart.js"
    );
    addToCart(block);
    return false;
  }
  // Navter Structure Decorate called start
  if (window.location.href.includes("download")) {
    const path = window.location.href.split("/").at(-1);
    if (path.includes("download")) {
      if (window.location.pathname.includes("/pms")) {
        window.location.href = `${window.location.origin}/pms/downloads/document-disclosure`;
      } else if (window.location.pathname.includes("/aif")) {
        window.location.href = `${window.location.origin}/aif/downloads/regulatory-updates`;
      } else {
        window.location.href = `${window.location.origin}/${path}/sid`;
      }
      return false;
    }
  }
  if (block.closest(".navter-section")) {
    const { default: navterdecrate } = await import(
      "../navter-filter-block/navter-filter-block.js"
    );
    navterdecrate(block);
    return false;
  }
  // NavterStructure Decorate called end

  if (block.closest(".section").getAttribute("data-id") === "downloadsec") {
    block
      .closest("body")
      .querySelector("footer")
      .classList.add("downloads-open");
    block.querySelectorAll("img").forEach((img) => {
      img.setAttribute("alt", "");
    });
    dataMapMoObj.dropEvent = "";
    dataMapMoObj.downloadCode(block);
    if (!window.location.pathname.includes(".risk-adjusted-return")) {
      dataMapMoObj.dropdownload(block);
    }
    dataMapMoObj.searchfunc(block);

    // PDF popup - 4 options on .pdf-icon click inside .pdf-list (event delegation)
    const downloadCont = block.querySelector(".download-container");
    if (downloadCont) {
      downloadCont.addEventListener(
        "click",
        (e) => {
          // If click is inside an open popup, let it handle
          if (e.target.closest(".pdf-action-popup")) return;

          // For grouped icons (Scheme Summary), target individual .anchorimg
          const anchorImg = e.target.closest(".pdf-icon-group .anchorimg");
          const pdfIcon =
            anchorImg || e.target.closest(".pdf-icon:not(.pdf-icon-group)");

          if (!pdfIcon) {
            downloadCont
              .querySelectorAll(".pdf-action-popup.is-open")
              .forEach((p) => p.classList.remove("is-open"));
            return;
          }

          // Stop default behavior - only open popup, nothing else
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();

          // Determine the file URL based on context
          let pdfUrl = "";
          if (anchorImg) {
            // For grouped icons, get href from the clicked anchor itself
            pdfUrl = anchorImg.getAttribute("href") || "";
            anchorImg.onclick = (ev) => ev.preventDefault();
          } else {
            // For single icon, get href from the anchor inside
            const anchor = pdfIcon.querySelector("a");
            if (anchor) {
              pdfUrl = anchor.getAttribute("href") || "";
              anchor.onclick = (ev) => ev.preventDefault();
            }
          }

          // Element to return keyboard focus to once the popup closes
          const trigger = anchorImg || pdfIcon.querySelector("a") || pdfIcon;

          const closePopupAndRefocus = (popupEl) => {
            popupEl.classList.remove("is-open");
            trigger?.focus?.();
          };

          // Close other open popups
          downloadCont
            .querySelectorAll(".pdf-action-popup.is-open")
            .forEach((p) => {
              if (!pdfIcon.contains(p)) p.classList.remove("is-open");
            });

          let popup = pdfIcon.querySelector(".pdf-action-popup");
          if (!popup) {
            popup = document.createElement("div");
            popup.className = "pdf-action-popup";
            // Announce something meaningful when the popup receives focus,
            // since it's otherwise an unlabeled container.
            const fileLabel = pdfIcon
              .querySelector("img")
              ?.alt?.replace(/\s*pdf$/i, "")
              .trim();
            popup.setAttribute("role", "menu");
            popup.setAttribute(
              "aria-label",
              fileLabel ? `Document actions for ${fileLabel}` : "Document actions",
            );
            popup.setAttribute("tabindex", "-1");
            popup.innerHTML = `
            <div class="popup-options" role="none">
              <button class="popup-option" data-action="download" role="menuitem" aria-label="Download document">
                <span class="popup-icon download-icon" aria-hidden="true"></span>
                <span class="popup-label">Download</span>
              </button>
              <button class="popup-option" data-action="show" role="menuitem" aria-label="View document">
                <span class="popup-icon view-icon" aria-hidden="true"></span>
                <span class="popup-label">View</span>
              </button>
              <button class="popup-option" data-action="whatsapp" role="menuitem" aria-label="Share document on WhatsApp">
                <span class="popup-icon whatsapp-icon" aria-hidden="true"></span>
                <span class="popup-label">WhatsApp</span>
              </button>
              <button class="popup-option" data-action="email" role="menuitem" aria-label="Email document">
                <span class="popup-icon email-icon" aria-hidden="true"></span>
                <span class="popup-label">Email</span>
              </button>
            </div>
            <button class="popup-close" aria-label="Close document actions menu">&#10005;</button>
          `;
            popup.addEventListener("keydown", (ev) => {
              if (ev.key === "Escape") {
                ev.preventDefault();
                ev.stopPropagation();
                closePopupAndRefocus(popup);
              }
            });
            popup.addEventListener("click", (ev) => {
              ev.preventDefault();
              ev.stopPropagation();
              // Close button
              if (ev.target.closest(".popup-close")) {
                closePopupAndRefocus(popup);
                return;
              }
              const btn = ev.target.closest(".popup-option");
              if (!btn) return;
              const action = btn.dataset.action;
              // Get the file URL fresh from the parent element's href
              const currentUrl =
                pdfIcon.getAttribute("href") ||
                pdfIcon.querySelector("a")?.getAttribute("href") ||
                pdfUrl;
              const url = window.location.origin + currentUrl;
              switch (action) {
                case "download":
                  if (currentUrl) {
                    fetch(currentUrl)
                      .then((response) => {
                        if (!response.ok) throw new Error("Network error");
                        return response.blob();
                      })
                      .then((blob) => {
                        const blobUrl = window.URL.createObjectURL(blob);
                        const alink = document.createElement("a");
                        alink.style.display = "none";
                        alink.href = blobUrl;
                        alink.download = currentUrl.split("/").pop();
                        alink.target = "_blank";
                        document.body.appendChild(alink);
                        alink.click();
                        setTimeout(() => {
                          window.URL.revokeObjectURL(blobUrl);
                          alink.remove();
                        }, 100);
                      })
                      .catch(() => {
                        window.open(currentUrl, "_blank");
                      });
                  }
                  break;
                case "show":
                  if (currentUrl) {
                    const viewWindow = window.open(currentUrl, "_blank");
                    if (!viewWindow) {
                      // Fallback if popup blocker prevents it
                      const alink = document.createElement("a");
                      alink.href = currentUrl;
                      alink.target = "_blank";
                      alink.rel = "noopener noreferrer";
                      document.body.appendChild(alink);
                      alink.click();
                      alink.remove();
                    }
                  }
                  break;
                case "whatsapp":
                  window.open(
                    `https://wa.me/?text=${encodeURIComponent(url || window.location.href)}`,
                    "_blank",
                  );
                  break;
                case "email":
                  window.location.href = `mailto:?subject=Document&body=${encodeURIComponent(url || window.location.href)}`;
                  break;
                default:
                  break;
              }
              closePopupAndRefocus(popup);
            });
            pdfIcon.style.position = "relative";
            pdfIcon.appendChild(popup);
          }
          popup.classList.toggle("is-open");
          if (popup.classList.contains("is-open")) {
            setTimeout(() => {
              popup.querySelector(".popup-option")?.focus();
            }, 50);
          } else {
            trigger?.focus?.();
          }
        },
        true,
      ); // Use capture phase to intercept before other handlers

      document.addEventListener("click", (e) => {
        if (
          !e.target.closest(".pdf-icon") &&
          !e.target.closest(".pdf-icon-group .anchorimg")
        ) {
          downloadCont
            .querySelectorAll(".pdf-action-popup.is-open")
            .forEach((p) => p.classList.remove("is-open"));
        }
      });
    }
    return false;
  }


  // Use shared lazy-loading getListing function
  if (listingData === null) {
    listingData = await getFundListings();
  }

  const etfOrderMap = new Map();
  const indexOrderMap = new Map();

  listingData.etfFundsListing?.forEach((item, index) => {
    const schemeName = item.split(":")[0].trim();

    etfOrderMap.set(schemeName, index);
  });

  listingData.indexFundsListing?.forEach((item, index) => {
    const schemeName = item.split(":")[0].trim();
    indexOrderMap.set(schemeName, index);
  });

  window.etfOrderMap = etfOrderMap;
  window.indexOrderMap = indexOrderMap;

  // Hide CAGR/returns for specific funds (but still show the fund cards) AJ27
  const tempZeroReturn = [
    "Motilal Oswal Consumption Fund",
    "Motilal Oswal Infrastructure Fund",
    "Motilal Oswal Services Fund",
    "Motilal Oswal Special Opportunities Fund",
    "Motilal Oswal Nifty 100 ETF",
    "Motilal Oswal Nifty 50 Equal Weight ETF",
  ];
  listingData.cfDataObjs.forEach((el) => {
    if (tempZeroReturn.includes(el.schemeName)) {
      el.hideReturns = true;
    }
  });
  // AJ27
  // const nfofund = listingData.cfDataObjs.filter((nfo) => {
  //   const funnfo = getFundStatus(nfo);
  //   if (!funnfo.isNFO && nfo.fundsTaggingSection.includes('motilal-oswal-amc:nfo')) {
  //     const indexval = nfo.fundsTaggingSection.indexOf('motilal-oswal-amc:nfo');
  //     nfo.fundsTaggingSection.splice(indexval, 1);
  //   }
  //   if (funnfo.isNFO && !funnfo.investEnabled && nfo.fundsTaggingSection.includes('motilal-oswal-amc:nfo')) {
  //     listingData.cfDataObjs = listingData.cfDataObjs.filter((el, indexval) => listingData.cfDataObjs.indexOf(nfo) !== indexval);
  //   }
  //   return funnfo.isNFO && nfo.fundsTaggingSection.includes('motilal-oswal-amc:nfo');
  // });
  // if (nfofund.length !== 0) {
  //   const fundstatus = getFundStatus(nfofund[0]);
  //   if (nfofund.length !== 0 && !fundstatus.isNFO && [...nfofund[0].fundsTaggingSection].includes('motilal-oswal-amc:nfo')) {
  //     const tags = nfofund[0].fundsTaggingSection.filter((item) => item !== 'motilal-oswal-amc:nfo');
  //     nfofund[0].fundsTaggingSection = tags || [];
  //   }
  // }

  // 1. First, modify the tags for items that are no longer NFOs
  listingData.cfDataObjs.forEach((nfo) => {
    const funnfo = getFundStatus(nfo);
    if (
      !funnfo.isNFO &&
      nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
    ) {
      const indexval = nfo.fundsTaggingSection.indexOf("motilal-oswal-amc:nfo");
      nfo.fundsTaggingSection.splice(indexval, 1);
    }
  });

  // 2. Now, filter the main list to REMOVE non-investable NFOs
  // and assign the remaining NFOs to your variable.
  listingData.cfDataObjs = listingData.cfDataObjs.filter((nfo) => {
    const funnfo = getFundStatus(nfo);
    const hasNfoTag = nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo");

    // If it's an NFO but investment is disabled, return false to REMOVE it from cfDataObjs
    if (funnfo.isNFO && !funnfo.investEnabled) {
      return false;
    }

    // Keep everything else in cfDataObjs
    return true;
  });

  // 3. Finally, get your specific subset of NFO funds from the cleaned list
  const nfofund = listingData.cfDataObjs.filter((nfo) => {
    const funnfo = getFundStatus(nfo);
    return (
      funnfo.isNFO && nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
    );
  });
  if (nfofund.length !== 0) {
    const listcf = listingData.cfDataObjs.filter((filterel) => {
      const tags = filterel.fundsTaggingSection;
      if (!tags) return true; // Keep the item if there are no tags to check
      return filterel.schcode !== nfofund[0].schcode;
    });
    listingData.cfDataObjs = listcf;
    // if (shouldShowCard(nfofund)) {
    listingData.cfDataObjs = appendUniqueFunds(
      listingData.cfDataObjs,
      nfofund,
    );
    // }
  }
  const ultooltip = block.closest(".section");
  const ullisttoop = ultooltip.querySelector(".default-content-wrapper ul");
  // console.log(ullisttoop);
  Array.from(block.closest(".section").children).forEach((el, index) => {
    el.classList.add(`item${index + 1}`);
  });
  Array.from(block.children).forEach((el, index) => {
    el.classList.add(`block-item${index + 1}`);
    Array.from(el.children).forEach((elsub, indexsub) => {
      elsub.classList.add(`block-subitem${indexsub + 1}`);
      Array.from(elsub.children).forEach((finelsub, indexin) => {
        finelsub.classList.add(`block-subitem-finelsub${indexin + 1}`);
      });
    });
  });

  // start
  const mainElementKyc = block?.closest("main");

  if (mainElementKyc && block.closest(".kyc-imp-points")) {
    const kycPointList = mainElementKyc.querySelectorAll(
      ".section.kyc-imp-points .our-funds-block .block-subitem-finelsub2",
    );

    if (kycPointList.length > 0) {
      dataMapMoObj.CLASS_PREFIXES = [
        "kyc-point-upper",
        "kyc-point-mid",
        "kyc-point-inner",
        "kyc-point-detail",
      ];

      kycPointList.forEach((element) => {
        dataMapMoObj.addIndexed(element);
      });

      // console.log(`Successfully indexed ${kycPointList.length} elements.`);
    }
  }
  // end
  if (
    block.closest(".section")?.querySelector(".item2")?.children !== undefined
  ) {
    Array.from(
      block.closest(".section")?.querySelector(".item2")?.children,
    ).forEach((el) => {
      el.classList.add("list-header-text");
    });
    block.closest(".section").querySelector(".item2 ul")?.remove();
  }
  if (
    block.querySelector(".block-item3 .block-subitem-finelsub4")?.children !==
    undefined
  ) {
    Array.from(
      block.querySelector(".block-item3 .block-subitem-finelsub4")?.children,
    ).forEach((el) => {
      el.classList.add("viewlist-btn");
      el.querySelectorAll("img").forEach((imgEl) => {
        imgEl.setAttribute("alt", "");
      });
    });
  }
  if (
    block.querySelector(".block-item3 .block-subitem-finelsub5")?.children !==
    undefined
  ) {
    Array.from(
      block.querySelector(".block-item3 .block-subitem-finelsub5").children,
    ).forEach((el) => {
      el.classList.add("viewlist-btn");
      el.querySelectorAll("img").forEach((imgEl) => {
        imgEl.setAttribute("alt", "");
      });
    });
  }
  dataMapMoObj.selectreturns = "";
  const tempDfilt = listingData?.cfDataObjs?.filter((el) => {
    if (!el.fundsTaggingSection || !el.planList) {
      return false;
    }
    return el;
  });
  dataMapMoObj.data = dataFilterfun(tempDfilt);
  dataMapMoObj.datatooltip = {};
  Array.from(ullisttoop.children).forEach((tooltip) => {
    const datakey = tooltip.textContent.trim().split(":-");
    const datkey = datakey[0];
    const datval = datakey[1];
    if (datkey === "Active") {
      dataMapMoObj.datatooltip.active = datval;
    } else if (datkey === "Commodity") {
      dataMapMoObj.datatooltip.commodity = datval;
    } else if (datkey === "Debt & Liquid") {
      dataMapMoObj.datatooltip["debt-&-liquid"] = datval;
    } else if (datkey === "ETFs") {
      dataMapMoObj.datatooltip.etf = datval;
    } else if (datkey === "Factor") {
      dataMapMoObj.datatooltip["indian-equity"] = datval;
    } else if (datkey === "Hybrid & Balanced") {
      dataMapMoObj.datatooltip["hybrid-&-balanced"] = datval;
    } else if (datkey === "Index Funds") {
      dataMapMoObj.datatooltip["index-funds"] = datval;
    } else if (datkey === "Indian Equity") {
      dataMapMoObj.datatooltip["indian-equity"] = datval;
    } else if (datkey === "International Equity") {
      dataMapMoObj.datatooltip["international-equity"] = datval;
    } else if (datkey === "Mid Cap") {
      dataMapMoObj.datatooltip["indian-equity"] = datval;
    } else if (datkey === "Multi Asset") {
      dataMapMoObj.datatooltip["multi-asset"] = datval;
    } else if (datkey === "Multi Cap Fund") {
      dataMapMoObj.datatooltip["indian-equity"] = datval;
    } else if (datkey === "Sector") {
      dataMapMoObj.datatooltip["indian-equity"] = datval;
    } else if (datkey === "Small Cap") {
      dataMapMoObj.datatooltip["indian-equity"] = datval;
    }
  });
  let checkboxSel = "";
  let funddata;

  // Run this on page load on the destination domain
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('viewmark')) {
    localStorage.setItem('viewmark', urlParams.get('viewmark'));
    if (urlParams.has('selectedFund')) {
      localStorage.setItem('selectedFund', urlParams.get('selectedFund'));
    }

    const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl);
  }

  if (localStorage.getItem("viewmark")) {
    const fundlast = dataMapMoObj.data.fundCategory;
    const indiansub = fundlast[fundlast.length - 1];
    checkboxSel = localStorage.getItem("viewmark");
    console.log("sdfghygfdsasdfg65432345678", checkboxSel);

    localStorage.removeItem("viewmark");
    if (checkboxSel === "trending-funds") {
      const shcodeArr = listingData.trendingFunds.map((el) => el.split(":")[1]);
      const tempDfiltTrending = listingData.cfDataObjs.filter((el) => {
        if (!el.fundsTaggingSection || !el.planList) return false;
        return shcodeArr.includes(el.schcode);
      });
      const nfoAll = listingData.cfDataObjs.filter((f) => {
        const status = getFundStatus(f);
        return (
          status.isNFO &&
          f.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        );
      });
      const nonNfo = tempDfiltTrending.filter((f) => {
        const status = getFundStatus(f);
        return !(
          status.isNFO &&
          f.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        );
      });
      dataMapMoObj.funddata = [...nfoAll, ...nonNfo];
      funddata = shcodeArr;
      checkboxSel = "";
    } else {
      dataMapMoObj.data.fundCategory.forEach((el) => {
        if (el[checkboxSel]) {
          funddata = el[checkboxSel];
        }
      });
      dataMapMoObj.data.fundType.forEach((el) => {
        if (el[checkboxSel]) {
          funddata = el[checkboxSel];
        }
      });
      indiansub.indianEquitySub.forEach((el) => {
        if (el[checkboxSel]) {
          funddata = el[checkboxSel];
        }
      });
      if (funddata !== undefined) {
        const tempDfilttweleve = listingData.cfDataObjs.filter((el) => {
          if (!el.fundsTaggingSection || !el.planList) {
            return false;
          }
          return el;
        });
        dataMapMoObj.funddata = tempDfilttweleve.filter((el) =>
          funddata.includes(el.schcode),
        );
      }
    }
  }
  if (funddata === undefined) {
    const popular = listingData.mostBoughtFunds.map((el) => el.split(":")[0]);
    const tempDfiltthirdh = listingData.cfDataObjs.filter((el) => {
      if (!popular.includes(el.schemeName)) {
        return false;
      }
      return el;
    });
    dataMapMoObj.funddata = tempDfiltthirdh.slice(0, 10);
    if (
      !dataMapMoObj.funddata[0].fundsTaggingSection.includes(
        "motilal-oswal-amc:nfo",
      )
    ) {
      const nfofundv2 = listingData.cfDataObjs.filter((nfo) => {
        const funnfo = getFundStatus(nfo);
        if (
          !funnfo.isNFO &&
          nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        ) {
          const indexval = nfo.fundsTaggingSection.indexOf(
            "motilal-oswal-amc:nfo",
          );
          nfo.fundsTaggingSection.splice(indexval, 1);
        }
        if (
          funnfo.isNFO &&
          !funnfo.investEnabled &&
          nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        ) {
          listingData.cfDataObjs = listingData.cfDataObjs.filter(
            (el, indexval) => listingData.cfDataObjs.indexOf(nfo) !== indexval,
          );
        }
        return (
          funnfo.isNFO &&
          nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
        );
      });
      if (nfofundv2.length !== 0) {
        const fundstatusv2 = getFundStatus(nfofundv2[0]);
        if (
          nfofundv2.length !== 0 &&
          !fundstatusv2.isNFO &&
          [...nfofundv2[0].fundsTaggingSection].includes(
            "motilal-oswal-amc:nfo",
          )
        ) {
          const tags = nfofundv2[0].fundsTaggingSection.filter(
            (item) => item !== "motilal-oswal-amc:nfo",
          );
          nfofundv2[0].fundsTaggingSection = tags || [];
        }
        dataMapMoObj.funddata = dataMapMoObj.funddata.filter((filterel) => {
          const tags = filterel.fundsTaggingSection;
          if (!tags) return true; // Keep the item if there are no tags to check
          return tags.schcode !== nfofundv2[0].schcode;
        });
        // if (shouldShowCard(nfofundv2)) {
        dataMapMoObj.funddata.unshift(...nfofundv2);
        // }
      }
    }
  }
  const subfourer = block.querySelector(".block-subitem2");
  const subun = subfourer.querySelector(".block-subitem-finelsub3 span");
  const subfour = subun.cloneNode(true);
  const etfarry = [];
  const notetfarry = [];
  dataMapMoObj.funddata.forEach((el) => {
    if (
      !el.fundsTaggingSection.includes("motilal-oswal-amc:nfo") &&
      el.fundsTaggingSection.includes("motilal-oswal-amc:etf")
    ) {
      etfarry.push(el);
    } else {
      notetfarry.push(el);
    }
  });
  // ETFs hidden on initial load (no checkbox checked)
  dataMapMoObj.funddata = [...notetfarry];
  const divfund = div(
    {
      class: "blockwrapper",
    },
    div(
      {
        class: "upper-container",
      },
      div(
        {
          class: "fundcontainer",
        },
        block.querySelector(".block-subitem1"),
        div(
          {
            class: "search-trending-wrapper",
          },
          div(
            {
              class: "search-input",
            },
            label(
              {
                for: "search-field", // Use a valid ID
                class: "search-label",
              },
              "Search here",
            ),
            span(
              {
                class: "sr-only",
                id: "search-field-hint",
              },
              "Suggestions will appear as you start typing. Use the arrow keys to browse them.",
            ),
            input({
              class: "search",
              id: "search-field",
              "aria-describedby": "search-field-hint search-field-status",
              placeholder: block
                .querySelector(".block-subitem2 .block-subitem-finelsub1")
                .textContent.trim(),
            }),
            span(
              {
                class: "sr-only",
                id: "search-field-status",
                role: "status",
                "aria-live": "polite",
              },
              "",
            ),
            button(
              {
                class: "cancel-search",
                type: "button",
                "aria-label": "Clear search",
              },
              img({
                class: "cancel-btn",
                src: "/icons/input-cancel.svg",
                alt: "clear",
                fetchpriority: "high",
                loading: "eager",
              }),
            ),
            ul(
              {
                class: "list-search",
              },
              ...dataMapMoObj.funddata.map((el) => {
                const base = `${window.location.origin}/mutual-funds`;
                let slug = el.schemeName?.split("/");
                slug = slug?.at(-1);
                slug = slug?.toLowerCase().replace(/\s+/g, '-');
                const href = `${base}/${slug}`;
                return li(
                  {
                    class: "list-fund-name",
                    schcode: el.schcode,
                    "data-original-text": el.schemeName,
                  },
                  a({ href }, el.schemeName),
                );
              }),
            ),
          ),
          div(
            {
              class: "watchlist",
            },
            div(
              {
                class: "staricon",
              },
              block.querySelector(
                ".block-subitem2 .block-subitem-finelsub2 span",
              ),
              // block.querySelector(
              //   '.block-subitem2 .block-subitem-finelsub3 span',
              // ),
            ),
            div(
              {
                class: "watchlisttext",
              },
              span(
                block
                  .querySelector(".block-subitem2 .block-subitem-finelsub2")
                  .textContent.trim(),
              ),
            ),
          ),
          div(
            {
              class: "trending-container",
            },
            div(
              {
                class: "trendinglabel",
              },
              p(subfour),
              span(
                {
                  class: "trending-text",
                },
                block
                  .querySelector(".block-subitem2 .block-subitem-finelsub4")
                  .textContent.trim(),
              ),
            ),
            (() => {
              const trendingDiv = div({ class: "trendingmostlist" });
              const trendingSchcodes = listingData.trendingFunds.map(
                (el) => el.split(":")[1],
              );
              const trendingFunds = listingData.cfDataObjs.filter(
                (el) =>
                  el.fundsTaggingSection &&
                  el.planList &&
                  trendingSchcodes.includes(el.schcode),
              );
              const nfoFundsAll = listingData.cfDataObjs.filter((f) => {
                const status = getFundStatus(f);
                return (
                  status.isNFO &&
                  f.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
                );
              });
              const nonNfoTrending = trendingFunds.filter((f) => {
                const status = getFundStatus(f);
                return !(
                  status.isNFO &&
                  f.fundsTaggingSection.includes("motilal-oswal-amc:nfo")
                );
              });
              const orderedFunds = [...nfoFundsAll, ...nonNfoTrending];
              const trendingUl = document.createElement("ul");
              trendingUl.className = "block-subitem-finelsub5";
              orderedFunds.forEach((fund) => {
                let linkredirection = `${window.location.origin}/mutual-funds/${fund.schemeName}`;
                if (fund.fundsUrl) {
                  linkredirection = fund.fundsUrl.replace('/content/moamc-eds/mutual-fund/in/en', '');
                }
                const liEl = document.createElement("li");
                const aEl = document.createElement("a");
                aEl.href = linkredirection;
                aEl.textContent = fund.schemeName;
                liEl.appendChild(aEl);
                trendingUl.appendChild(liEl);
              });
              trendingDiv.appendChild(trendingUl);
              return trendingDiv;
            })(),
          ),
        ),
      ),
    ),
    div(
      {
        class: "filter-cards",
      },
      div(
        {
          class: "left-container",
        },
        div(
          {
            class: "fundcategory-container",
          },
          div(
            {
              class: "filter-sort-container",
            },
            div(
              {
                class: "filter-wrapper",
                onclick: () => {
                  block
                    .querySelector(".filter-overlay")
                    .classList.add("active");
                  if (window.innerWidth < 768) {
                    block.closest("body").classList.add("scroll-lock");
                  }
                  if (
                    Array.from(
                      block.querySelector(".sort-overlay").classList,
                    ).includes("active")
                  ) {
                    block
                      .querySelector(".sort-overlay")
                      .classList.remove("active");
                  }
                },
              },
              div(
                {
                  class: "filter-text",
                },
                block.querySelector(
                  ".block-item2 .block-subitem-finelsub1 span",
                ),
                h2(
                  block
                    .querySelector(".block-item2 .block-subitem-finelsub2")
                    .textContent.trim(),
                ),
              ),
              button(
                {
                  class: "clearall-btn",
                  "aria-label": "Clear All Filters",
                  onclick: () => {
                    block.closest("body").classList.remove("scroll-lock");
                    Array.from(
                      block.querySelector(".filter-list-wrapper").children,
                    ).forEach((el) => {
                      const container = el.closest(".checkbox-label-container");
                      if (
                        container &&
                        container.querySelector(".innerindianequity")
                      ) {
                        container
                          .querySelectorAll(".innerindianequity input")
                          .forEach((elemsub) => {
                            elemsub.checked = false;
                          });
                      }
                      const mainInput = el.querySelector("input");
                      if (mainInput) {
                        mainInput.checked = false;
                      }
                    });
                    const tempDfiltfourteen = listingData.cfDataObjs.filter(
                      (el) => {
                        if (!el.fundsTaggingSection || !el.planList) {
                          return false;
                        }
                        return el;
                      },
                    );
                    dataMapMoObj.funddata = tempDfiltfourteen.slice(0, 11);
                    viewFunction(block);
                    block.querySelector(".applied-filter-list").innerHTML = "";
                    block
                      .querySelector(".applied-filter-wrap")
                      .classList.remove("filter-active");
                    updateClearallButtonState(block);
                  },
                },
                "Clear All",
              ),
            ),
            div(
              {
                class: "sort-wrapper",
                onclick: () => {
                  block.querySelector(".sort-overlay").classList.add("active");
                  block.closest("body").classList.add("scroll-lock");
                  if (
                    Array.from(
                      block.querySelector(".filter-overlay").classList,
                    ).includes("active")
                  ) {
                    block
                      .querySelector(".filter-overlay")
                      .classList.remove("active");
                  }
                },
              },
              block.querySelector(".block-item2 .block-subitem-finelsub3 span"),
              p(
                block
                  .querySelector(".block-item2 .block-subitem-finelsub4")
                  .textContent.trim(),
              ),
            ),
          ),
          div(
            {
              class: "filter-overlay",
            },
            div(
              {
                class: "filter-container",
              },
              div(
                {
                  class: "clearall-wrapper",
                },
                span("Filters"),
                button(
                  {
                    class: "clearall-btn",
                    "aria-label": "Clear All Filters",
                    onclick: () => {
                      Array.from(
                        block.querySelector(".filter-list-wrapper").children,
                      ).forEach((el) => {
                        if (
                          el.closest(".checkbox-label-container") !== null &&
                          el
                            .closest(".checkbox-label-container")
                            .querySelector(".innerindianequity")
                        ) {
                          el.closest(".checkbox-label-container")
                            .querySelectorAll(".innerindianequity input")
                            .forEach((elemsub) => {
                              elemsub.checked = false;
                            });
                        }
                        if (el.querySelector("input") !== null) {
                          el.querySelector("input").checked = false;
                        }
                      });
                      const tempDfiltfivteen = listingData.cfDataObjs.filter(
                        (el) => {
                          if (!el.fundsTaggingSection || !el.planList) {
                            return false;
                          }
                          return el;
                        },
                      );
                      dataMapMoObj.funddata = tempDfiltfivteen.slice(0, 11);
                      updateClearallButtonState(block);
                    },
                  },
                  "Clear All",
                ),
              ),
              (() => {
                const normalizeTooltipId = (value) =>
                  (value || "")
                    .toString()
                    .trim()
                    .toLowerCase()
                    .replace(/&/g, "and")
                    .replace(/[^a-z0-9]+/g, "-")
                    .replace(/(^-|-$)/g, "") || "tooltip";
                const filterLabelOverrides = {
                  "Multi Cap Fund": "Multi Cap",
                  "Index Funds": "Index",
                };
                const getFilterLabel = (raw) =>
                  filterLabelOverrides[raw] || raw;
                return div(
                  {
                    class: "filter-list-wrapper",
                  },
                  span(
                    { class: "sr-only" },
                    "On selecting the checkbox, the main content will be updated",
                  ),
                  ...dataMapMoObj.data.fundCategory.map((element, index) => {
                    const indexeq =
                      Object.keys(element)[0] === "indian-equity"
                        ? "indaneqsub"
                        : "";
                    const tooltipId = `tooltip-${normalizeTooltipId(Object.keys(element)[0])}-${index + 1}`;
                    if (
                      capitalizeEachWord(
                        Object.keys(element)[0].replaceAll("-", " "),
                      ) === "Indian Equity"
                    ) {
                      dataMapMoObj[`${index}ArrayDoc`] = div(
                        {
                          class: "indian-equity-container",
                        },
                        ...dataMapMoObj.data.fundCategory[
                          dataMapMoObj.data.fundCategory.length - 1
                        ].indianEquitySub.map((elme, ind) => {
                          const sublabel = Object.keys(elme)[0].replaceAll(
                            "-",
                            " ",
                          );
                          return div(
                            {
                              class: "checkbox-label-container",
                              style: `display: ${elme[Object.keys(elme)[0]].length !== 0 ? "" : "none"}`,
                            },
                            input({
                              class: "category-direct",
                              type: "checkbox",
                              id: `ind${ind + 1}`,
                              dataattr: elme[Object.keys(elme)].join("-"),
                              datakey: Object.keys(elme)[0],
                              "aria-label": `Filter by ${capitalizeEachWord(sublabel)}`,
                              onchange: () => {
                                if (
                                  block.querySelector(".togglebtn").style
                                    .display !== "none" ||
                                  block.querySelector(".togglebtn").style
                                    .display !== ""
                                ) {
                                  block.querySelector(
                                    ".togglebtn",
                                  ).style.display = "flex";
                                }
                                if (
                                  block.querySelectorAll(
                                    '[type="checkbox"]:checked',
                                  ).length === 1 &&
                                  block
                                    .querySelectorAll(
                                      '[type="checkbox"]:checked',
                                    )[0]
                                    ?.nextSibling.querySelector("label")
                                    ?.textContent?.includes("ETF's")
                                ) {
                                  block.querySelector(
                                    ".togglebtn",
                                  ).style.display = "none";
                                } else {
                                  block.querySelector(
                                    ".togglebtn",
                                  ).style.display = "flex";
                                }
                                if (window.innerWidth < 786) {
                                  const temp = [];
                                  const dup = [];
                                  Array.from(
                                    block.querySelectorAll(
                                      ".checkbox-label-container input",
                                    ),
                                  ).forEach((el) => {
                                    if (el.checked) {
                                      const tempel = el
                                        .getAttribute("dataattr")
                                        .split("-");
                                      temp.push(...tempel);
                                    }
                                  });
                                  if (temp.length > 0) {
                                    temp.forEach((scel) => {
                                      if (!dup.includes(scel)) {
                                        dup.push(scel);
                                      }
                                    });
                                  }
                                  // console.log(dup);
                                  const tempdata =
                                    listingData.cfDataObjs.filter((el) =>
                                      dup.includes(el.schcode) ? el : "",
                                    );
                                  dataMapMoObj.tempMobReturn = [];
                                  dataMapMoObj.tempMobReturn = tempdata;
                                  updateClearallButtonState(block);
                                } else {
                                  checkfilter(block);
                                  updateClearallButtonState(block);
                                }
                              },
                              onkeydown: (event) => {
                                if (
                                  event.key === "Enter" ||
                                  event.key === " "
                                ) {
                                  event.preventDefault();
                                  event.target.checked = !event.target.checked;
                                  event.target.dispatchEvent(
                                    new Event("change", { bubbles: true }),
                                  );
                                }
                              },
                            }),
                            label(
                              {
                                for: `ind${ind + 1}`,
                              },
                              getFilterLabel(capitalizeEachWord(sublabel)),
                              span(
                                {
                                  class: "fund-length",
                                },
                                `(${elme[Object.keys(elme)[0]].length})`,
                              ),
                            ),
                          );
                        }),
                      );
                    }
                    const indetempcount =
                      Object.keys(element)[0] === "indian-equity"
                        ? element[Object.keys(element)[0]].length
                        : element[Object.keys(element)[0]].length;
                    const labelval = getFilterLabel(
                      Object.keys(element)[0] === "nfo"
                        ? Object.keys(element)[0].toUpperCase()
                        : capitalizeEachWord(
                          Object.keys(element)[0].replaceAll("-", " "),
                        ),
                    );
                    return Object.keys(element)[0] !== "indianEquitySub"
                      ? div(
                        {
                          class: `checkbox-label-container ${indexeq}`,
                          style: `display: ${element[Object.keys(element)[0]].length !== 0 ? "" : "none"}`,
                        },
                        Object.keys(element)[0] === "nfo"
                          ? div(
                            { class: "sr-only" },
                            "On selecting the checkbox, the main content will be updated",
                          )
                          : "",
                        input({
                          class: `category-direct ${Object.keys(element)[0]}`,
                          type: "checkbox",
                          id: `index${index + 1}`,
                          dataattr:
                            element[Object.keys(element)[0]].join("-"),
                          datakey: Object.keys(element)[0],
                          "aria-label": `Filter by ${labelval}`,
                          onchange: (event) => {
                            if (
                              block.querySelector(".togglebtn").style
                                .display !== "none" ||
                              block.querySelector(".togglebtn").style
                                .display !== ""
                            ) {
                              block.querySelector(
                                ".togglebtn",
                              ).style.display = "flex";
                            }
                            if (event.target.closest(".indaneqsub")) {
                              const el = event.target.closest(".indaneqsub");
                              if (el.querySelector(".innerindianequity")) {
                                el.querySelectorAll(
                                  ".innerindianequity input",
                                ).forEach((elemsub) => {
                                  elemsub.checked =
                                    el.querySelector("input").checked;
                                });
                              }
                            }
                            if (
                              block.querySelectorAll(
                                '[type="checkbox"]:checked',
                              ).length === 1 &&
                              block
                                .querySelectorAll(
                                  '[type="checkbox"]:checked',
                                )[0]
                                ?.nextSibling.querySelector("label")
                                ?.textContent?.includes("ETF's")
                            ) {
                              block.querySelector(
                                ".togglebtn",
                              ).style.display = "none";
                            } else {
                              block.querySelector(
                                ".togglebtn",
                              ).style.display = "flex";
                            }
                            if (window.innerWidth < 786) {
                              const temp = [];
                              const dup = [];
                              Array.from(
                                block.querySelectorAll(
                                  ".checkbox-label-container input",
                                ),
                              ).forEach((el) => {
                                if (el.checked) {
                                  const tempel = el
                                    .getAttribute("dataattr")
                                    .split("-");
                                  temp.push(...tempel);
                                }
                              });
                              if (temp.length > 0) {
                                temp.forEach((scel) => {
                                  if (!dup.includes(scel)) {
                                    dup.push(scel);
                                  }
                                });
                              }
                              // console.log(dup);
                              const tempDfiltsixteen =
                                listingData.cfDataObjs.filter((el) => {
                                  if (
                                    !el.fundsTaggingSection ||
                                    !el.planList
                                  ) {
                                    return false;
                                  }
                                  return el;
                                });
                              const tempdata = tempDfiltsixteen.filter(
                                (el) => (dup.includes(el.schcode) ? el : ""),
                              );
                              dataMapMoObj.tempMobReturn = [];
                              dataMapMoObj.tempMobReturn = tempdata;
                            } else {
                              checkfilter(block);
                            }
                            updateClearallButtonState(block);
                          },
                          onkeydown: (event) => {
                            if (event.key === "Enter" || event.key === " ") {
                              event.preventDefault();
                              event.target.checked = !event.target.checked;
                              event.target.dispatchEvent(
                                new Event("change", { bubbles: true }),
                              );
                            }
                          },
                        }),
                        div(
                          {
                            class: "label-tooltip-wrap",
                          },
                          label(
                            {
                              for: `index${index + 1}`,
                              class: `${Object.keys(element)[0]}`,
                            },
                            labelval,
                            span(
                              {
                                class: "fund-length",
                              },
                              `(${indetempcount})`,
                            ),
                          ),
                          div(
                            {
                              class: "tooltip-wrap",
                              style: `display: ${dataMapMoObj.datatooltip[Object.keys(element)[0]] === undefined ? "none" : "block"};`,
                            },
                            button(
                              {
                                class: "filter-info-btn",
                                type: "button",
                                "aria-describedby": tooltipId,
                              },
                              img({
                                src: "/icons/filter-info.svg",
                                alt: "Filter Info Icon",
                              }),
                            ),
                            div(
                              {
                                class: "tooltip-text",
                                id: tooltipId,
                                role: "tooltip",
                                style: "display:none",
                              },
                              dataMapMoObj.datatooltip[
                              Object.keys(element)[0]
                              ],
                            ),
                          ),
                        ),
                        capitalizeEachWord(
                          Object.keys(element)[0].replaceAll("-", " "),
                        ) === "Indian Equity"
                          ? div(
                            {
                              class: "innerindianequity",
                            },
                            dataMapMoObj[`${index}ArrayDoc`],
                          )
                          : "",
                      )
                      : "";
                  }),
                  ...dataMapMoObj.data.fundType.map((element, index) => {
                    const tooltipId = `tooltip-fundtype-${normalizeTooltipId(Object.keys(element)[0])}-${index + 1}`;
                    return div(
                      {
                        class: "checkbox-label-container",
                        style: `display: ${element[Object.keys(element)[0]].length !== 0 ? "" : "none"}`,
                      },
                      input({
                        class: "category-direct",
                        type: "checkbox",
                        id: `fundtype${index + 1}`,
                        dataattr: element[Object.keys(element)[0]].join("-"),
                        datakey: Object.keys(element)[0],
                        "aria-label": `Filter by ${capitalizeEachWord(Object.keys(element)[0].replaceAll("-", " "))}`,
                        onchange: () => {
                          // checkfilter(block);
                          if (
                            block.querySelectorAll('[type="checkbox"]:checked')
                              .length === 1 &&
                            block
                              .querySelectorAll('[type="checkbox"]:checked')[0]
                              ?.nextSibling.querySelector("label")
                              ?.textContent?.includes("ETF's")
                          ) {
                            block.querySelector(".togglebtn").style.display =
                              "none";
                          } else {
                            block.querySelector(".togglebtn").style.display =
                              "flex";
                          }
                          if (window.innerWidth < 786) {
                            const temp = [];
                            const dup = [];
                            Array.from(
                              block.querySelectorAll(
                                ".checkbox-label-container input",
                              ),
                            ).forEach((el) => {
                              if (el.checked) {
                                const tempel = el
                                  .getAttribute("dataattr")
                                  .split("-");
                                temp.push(...tempel);
                              }
                            });
                            if (temp.length > 0) {
                              temp.forEach((scel) => {
                                if (!dup.includes(scel)) {
                                  dup.push(scel);
                                }
                              });
                            }
                            // console.log(dup);
                            const tempDfiltseventeen =
                              listingData.cfDataObjs.filter((el) => {
                                if (!el.fundsTaggingSection || !el.planList) {
                                  return false;
                                }
                                return el;
                              });
                            const tempdata = tempDfiltseventeen.filter((el) =>
                              dup.includes(el.schcode) ? el : "",
                            );
                            dataMapMoObj.tempMobReturn = [];
                            dataMapMoObj.tempMobReturn = tempdata;
                          } else {
                            checkfilter(block);
                          }
                          updateClearallButtonState(block);
                          // viewFunction(block);
                        },
                        onkeydown: (event) => {
                          if (event.key === "Enter" || event.key === " ") {
                            event.preventDefault();
                            event.target.checked = !event.target.checked;
                            event.target.dispatchEvent(
                              new Event("change", { bubbles: true }),
                            );
                          }
                        },
                      }),
                      div(
                        {
                          class: "label-tooltip-wrap",
                        },
                        label(
                          {
                            for: `fundtype${index + 1}`,
                          },
                          getFilterLabel(
                            capitalizeEachWord(
                              Object.keys(element)[0].replaceAll("-", " "),
                            ),
                          ),
                          span(`(${element[Object.keys(element)[0]].length})`),
                        ),
                        div(
                          {
                            class: "tooltip-wrap",
                            style: `display: ${dataMapMoObj.datatooltip[Object.keys(element)[0]] === undefined ? "none" : "block"};`,
                          },
                          button(
                            {
                              class: "filter-info-btn",
                              type: "button",
                              "aria-describedby": tooltipId,
                            },
                            img({
                              src: "/icons/filter-info.svg",
                              alt: "Filter Info Icon",
                            }),
                          ),
                          div(
                            {
                              class: "tooltip-text",
                              id: tooltipId,
                              role: "tooltip",
                              style: "display:none",
                            },
                            dataMapMoObj.datatooltip[Object.keys(element)[0]],
                          ),
                        ),
                      ),
                    );
                  }),
                );
              })(),
              div(
                {
                  class: "apply-wrapper",
                },
                button(
                  {
                    class: "close-btn",
                    onclick: () => {
                      block
                        .querySelector(".filter-overlay")
                        .classList.remove("active");
                      block.closest("body").classList.remove("scroll-lock");
                      block
                        .querySelector(".sort-overlay")
                        .classList.remove("active");
                    },
                  },
                  "Close",
                ),
                button(
                  {
                    class: "apply-btn",
                    onclick: () => {
                      block.closest("body").classList.remove("scroll-lock");
                      applyFunction(block);
                    },
                  },
                  "Apply",
                ),
              ),
            ),
          ),
          div(
            {
              class: "sort-overlay",
            },
            div(
              {
                class: "sort-container",
              },
              div(
                {
                  class: "sort-label",
                },
                // span(label(
                //   block.querySelector(".block-item3 .block-subitem-finelsub1").textContent.trim()
                // ))
                span(
                  block
                    .querySelector(".block-item3 .block-subitem-finelsub3")
                    .textContent.trim(),
                ),
              ),
              div(
                {
                  class: "arrange-returns",
                },
                div(
                  {
                    class: "arrange-container",
                    role: "radiogroup",
                    "aria-label": "Arrange by options",
                  },
                  span("Arrange by"),
                  div(
                    {
                      class: "radio-label-container",
                    },
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "popular",
                        name: "arrange",
                      }),
                      label(
                        {
                          for: "popular",
                        },
                        "Popular",
                      ),
                    ),
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "oldnew",
                        name: "arrange",
                      }),
                      label(
                        {
                          for: "oldnew",
                        },
                        "Oldest to Newest",
                      ),
                    ),
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "newold",
                        name: "arrange",
                      }),
                      label(
                        {
                          for: "newold",
                        },
                        "Newest to Oldest",
                      ),
                    ),
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "lastnav",
                        name: "arrange",
                      }),
                      label(
                        {
                          for: "lastnav",
                        },
                        "By Returns",
                      ),
                    ),
                  ),
                ),
                div(
                  {
                    class: "return-container",
                    role: "radiogroup",
                    "aria-label": "Returns period options",
                  },
                  span("Returns Period"),
                  div(
                    {
                      class: "radio-label-container",
                    },
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "sinceinp",
                        name: "returns",
                        dataattr:
                          dataMapMoObj.data.sort[0].inception_Ret.join("-"),
                      }),
                      label(
                        {
                          for: "sinceinp",
                        },
                        "Since Inception",
                      ),
                    ),
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "oneyear",
                        name: "returns",
                        dataattr:
                          dataMapMoObj.data.sort[0].oneYear_Ret.join("-"),
                      }),
                      label(
                        {
                          for: "oneyear",
                        },
                        "1 year",
                      ),
                    ),
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "threeyear",
                        name: "returns",
                        dataattr:
                          dataMapMoObj.data.sort[0].threeYear_Ret.join("-"),
                      }),
                      label(
                        {
                          for: "threeyear",
                        },
                        "3 years",
                      ),
                    ),
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "fiveyear",
                        name: "returns",
                        dataattr:
                          dataMapMoObj.data.sort[0].fiveYear_Ret.join("-"),
                      }),
                      label(
                        {
                          for: "fiveyear",
                        },
                        "5 years",
                      ),
                    ),
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "tenyear1",
                        name: "returns",
                        dataattr:
                          dataMapMoObj.data.sort[0].sevenYear_Ret.join("-"),
                      }),
                      label(
                        {
                          for: "tenyear1",
                        },
                        "7 years",
                      ),
                    ),
                    div(
                      {
                        class: "radio-label",
                      },
                      input({
                        type: "radio",
                        id: "tenyear2",
                        name: "returns",
                        dataattr:
                          dataMapMoObj.data.sort[0].tenYear_Ret.join("-"),
                      }),
                      label(
                        {
                          for: "tenyear2",
                        },
                        "10 years",
                      ),
                    ),
                  ),
                ),
              ),
              div(
                {
                  class: "close-apply-btn",
                },
                button(
                  {
                    class: "closebtn",
                    onclick: () => {
                      block
                        .querySelector(".filter-overlay")
                        .classList.remove("active");
                      block.closest("body").classList.remove("scroll-lock");
                      block
                        .querySelector(".sort-overlay")
                        .classList.remove("active");
                    },
                  },
                  "Close",
                ),
                button(
                  {
                    class: "applybtn",
                    onclick: () => {
                      block.closest("body").classList.remove("scroll-lock");
                      applyFunction(block);
                    },
                  },
                  "Apply",
                ),
              ),
            ),
          ),
        ),
      ),
      div(
        {
          class: "right-container",
        },
        div(
          {
            class: "sort-pop-container",
          },
          div(
            {
              class: "sort-popular",
            },
            div(
              {
                class: "sort-container",
              },
              span(
                {
                  class: "sort-pop-label",
                  id: "sort-pop-header-label",
                },
                block
                  .querySelector(".block-item3 .block-subitem-finelsub1")
                  .textContent.trim(),
              ),
              div(
                {
                  class: "sort-select-container",
                },
                p(
                  {
                    class: "selectedtext",
                    role: "combobox",
                    tabindex: "0",
                    "aria-labelledby": "sort-pop-header-label",
                    "aria-haspopup": "listbox",
                    "aria-expanded": "false", // Track expanded state programmatically
                    "aria-controls": "sortSelect",
                    onclick: (event) => {
                      // if (
                      //   Array.from(
                      //     event.target.nextElementSibling.classList,
                      //   ).includes("dropdown-active")
                      // ) {
                      //   event.target.nextElementSibling.classList.remove(
                      //     "dropdown-active",
                      //   );
                      // } else {
                      //   event.target.nextElementSibling.classList.add(
                      //     "dropdown-active",
                      //   );
                      // }
                      const target = event.target.closest(".selectedtext");
                      const listbox = target.nextElementSibling;
                      const isOpen = Array.from(listbox.classList).includes(
                        "dropdown-active",
                      );
                      if (isOpen) {
                        listbox.classList.remove("dropdown-active");
                        target.setAttribute("aria-expanded", "false");
                      } else {
                        listbox.classList.add("dropdown-active");
                        target.setAttribute("aria-expanded", "true");
                      }
                    },
                    onkeydown: (event) => {
                      const target = event.target.closest(".selectedtext");
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        // if (
                        //   Array.from(
                        //     event.target.nextElementSibling.classList,
                        //   ).includes("dropdown-active")
                        // ) {
                        //   event.target.nextElementSibling.classList.remove(
                        //     "dropdown-active",
                        //   );
                        // } else {
                        //   event.target.nextElementSibling.classList.add(
                        //     "dropdown-active",
                        //   );
                        // }
                        const listbox = target.nextElementSibling;
                        const isOpen = Array.from(listbox.classList).includes(
                          "dropdown-active",
                        );
                        if (isOpen) {
                          listbox.classList.remove("dropdown-active");
                          target.setAttribute("aria-expanded", "false");
                        } else {
                          listbox.classList.add("dropdown-active");
                          target.setAttribute("aria-expanded", "true");
                        }
                      } else if (event.key === "Escape") {
                        // event.target.nextElementSibling.classList.remove(
                        //   "dropdown-active",
                        // );
                        target.nextElementSibling.classList.remove(
                          "dropdown-active",
                        );
                        target.setAttribute("aria-expanded", "false");
                      }
                    },
                  },
                  "Popular",
                ),
                div(
                  {
                    class: "dropdown-list",
                    id: "sortSelect",
                    name: "sortSelect",
                    role: "listbox",
                    "aria-labelledby": "sort-pop-header-label",
                    onclick: (event) => {
                      // event.target
                      //   .closest(".dropdown-list")
                      //   .classList.remove("dropdown-active");
                      // const name = event.target.textContent.trim();
                      // event.target
                      //   .closest(".sort-select-container")
                      //   .querySelector("p").innerText = "";
                      // event.target
                      //   .closest(".sort-select-container")
                      //   .querySelector("p").innerText = name;
                      const listbox = event.target.closest(".dropdown-list");
                      listbox.classList.remove("dropdown-active");

                      // Collapse state on selection
                      const comboTrigger = listbox.previousElementSibling;
                      comboTrigger.setAttribute("aria-expanded", "false");

                      const name = event.target.textContent.trim();
                      comboTrigger.innerText = name;
                      if (!Array.isArray(dataMapMoObj.funddata) || dataMapMoObj.funddata.length === 0) {
                        dataMapMoObj.funddata = listingData.cfDataObjs.filter(
                          (fund) => fund?.fundsTaggingSection && fund?.planList,
                        );
                      }

                      // Reset all options to unselected, then select the clicked one
                      listbox
                        .querySelectorAll('[role="option"]')
                        .forEach((opt) => {
                          opt.setAttribute("aria-selected", "false");
                        });
                      event.target.setAttribute("aria-selected", "true");

                      if (name === "Popular") {
                        const popular = listingData.mostBoughtFunds.map(
                          (el) => el.split(":")[0],
                        );
                        const tempDfilteighteen = listingData.cfDataObjs.filter(
                          (el) => {
                            if (!popular.includes(el.schemeName)) {
                              return false;
                            }
                            return el;
                          },
                        );
                        // const nfofund = dataMapMoObj.getlisting.cfDataObjs.filter((nfo) =>
                        // nfo.fundsTaggingSection.includes('motilal-oswal-amc:nfo'));
                        dataMapMoObj.funddata = tempDfilteighteen.slice(0, 10); // .slice(0, 11);;
                        // if (nfofund.length !== 0) {
                        //   dataMapMoObj.funddata.unshift(...nfofund);
                        // }
                      }
                      if (
                        event.target.textContent.trim() === "Oldest to Newest"
                      ) {
                        const tempDfilttweefour = dataMapMoObj.funddata.filter(
                          (el) => {
                            if (!el.fundsTaggingSection || !el.planList) {
                              return false;
                            }
                            return el;
                          },
                        );
                        const tempData = JSON.parse(
                          JSON.stringify(tempDfilttweefour),
                        );
                        const tempa = tempData.sort(
                          (a, b) =>
                            new Date(a.dateOfAllotment) -
                            new Date(b.dateOfAllotment),
                        );
                        dataMapMoObj.funddata = tempa;
                      }
                      if (
                        event.target.textContent.trim() === "Newest to Oldest"
                      ) {
                        const tempDfiltninteen = dataMapMoObj.funddata.filter(
                          (el) => {
                            if (!el.fundsTaggingSection || !el.planList) {
                              return false;
                            }
                            return el;
                          },
                        );
                        const tempData = JSON.parse(
                          JSON.stringify(tempDfiltninteen),
                        );
                        const tempa = tempData.sort(
                          (a, b) =>
                            new Date(b.dateOfAllotment) -
                            new Date(a.dateOfAllotment),
                        );
                        dataMapMoObj.funddata = tempa;
                      }
                      if (event.target.textContent.trim() === "By Returns") {
                        const selectdrop =
                          dataMapMoObj.ObjTemp[
                          dataMapMoObj.objtempdrop[
                          dataMapMoObj.selectreturnstemp
                          ]
                          ];
                        const targetPlanName = Array.from(
                          block.querySelector(".togglebtn").classList,
                        ).includes("toggle-checked")
                          ? "Regular"
                          : "Direct";

                        const tempDfiltninteen = dataMapMoObj.funddata
                          .filter((fund) => fund?.planList?.length)
                          .sort(
                            (alist, blist) =>
                              getBestAvailableReturn(
                                blist,
                                targetPlanName,
                                selectdrop,
                              ) -
                              getBestAvailableReturn(
                                alist,
                                targetPlanName,
                                selectdrop,
                              ),
                          );
                        const tempa = JSON.parse(
                          JSON.stringify(tempDfiltninteen),
                        );
                        dataMapMoObj.funddata = tempa;
                      }
                      const searInp = block.querySelector(
                        ".search-input input",
                      );
                      searInp.value = "";
                      const cancelBtn = ensureCancelButton(
                        block.querySelector(".cancel-search"),
                      );
                      cancelBtn.style.display = "none";
                      const flitwrap = block.querySelector(
                        ".applied-filter-wrap",
                      );
                      // if (Array.from(flitwrap.classList).includes('filter-active')) {
                      //   flitwrap.classList.remove('filter-active');
                      // }
                      // Array.from(block.querySelector('.filter-list-wrapper').children).forEach((el) => {
                      //   if (el.closest('.checkbox-label-container') !== null && el.closest('.checkbox-label-container')?.querySelector('.innerindianequity')) {
                      //     el.closest('.checkbox-label-container').querySelectorAll('.innerindianequity input').forEach((elemsub) => {
                      //       if (elemsub.checked) {
                      //         elemsub.checked = false;
                      //       }
                      //     });
                      //   }
                      //   if (el.closest('.checkbox-label-container') !== null && el.querySelector('input').checked) {
                      //     // const moplabel = el.querySelector('input').nextElementSibling;
                      //     if (!Array.from(el.querySelector('input').classList).includes('indian-equity')) {
                      //       if (el.querySelector('input').checked) {
                      //         el.querySelector('input').checked = false;
                      //       }
                      //     } else {
                      //       el.querySelector('input').checked = false;
                      //     }
                      //   }
                      // });
                      block
                        .querySelectorAll(".arrange-container input")
                        .forEach((el) => {
                          el.checked = false;
                          if (el.nextElementSibling.textContent === name) {
                            el.checked = true;
                            el.dispatchEvent(
                              new Event("change", { bubbles: true }),
                            );
                          }
                          // if (el.nextElementSibling.textContent === name) {
                          //   el.click();
                          // }
                        });
                      viewFunction(block);
                      // planListEvent(event,block)
                    },
                  },
                  button(
                    {
                      "aria-label": "Sort by Popular",
                      role: "option",
                      "aria-selected": "true",
                    },
                    "Popular",
                  ),
                  button(
                    {
                      "aria-label": "Sort by Oldest to Newest",
                      role: "option",
                      "aria-selected": "false",
                    },
                    "Oldest to Newest",
                  ),
                  button(
                    {
                      "aria-label": "Sort by Newest to Oldest",
                      role: "option",
                      "aria-selected": "false",
                    },
                    "Newest to Oldest",
                  ),
                  button(
                    {
                      "aria-label": "Sort by Returns",
                      role: "option",
                      "aria-selected": "false",
                    },
                    "By Returns",
                  ),
                ),
              ),
            ),
            div(
              {
                class: "popular-container",
              },
              span(
                {
                  class: "sort-pop-label",
                },
                block
                  .querySelector(".block-item3 .block-subitem-finelsub2")
                  .textContent.trim(),
              ),
              div(
                {
                  class: "return-select-container",
                  id: "returns-period-header-label"
                },
                p(
                  {
                    class: "selectedtext",
                    role: "combobox",
                    tabindex: "0",
                    "aria-labelledby": "returns-period-header-label",
                    "aria-haspopup": "listbox",
                    "aria-expanded": "false",
                    "aria-controls": "returns-period-list",
                    onclick: (event) => {
                      const listbox = event.currentTarget.nextElementSibling;
                      const isOpen = Array.from(listbox.classList).includes(
                        "dropdown-active",
                      );
                      if (isOpen) {
                        listbox.classList.remove("dropdown-active");
                        event.currentTarget.setAttribute(
                          "aria-expanded",
                          "false",
                        );
                      } else {
                        listbox.classList.add("dropdown-active");
                        event.currentTarget.setAttribute(
                          "aria-expanded",
                          "true",
                        );
                      }
                    },
                    onkeydown: (event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        const listbox = event.currentTarget.nextElementSibling;
                        const isOpen = Array.from(listbox.classList).includes(
                          "dropdown-active",
                        );
                        if (isOpen) {
                          listbox.classList.remove("dropdown-active");
                          event.currentTarget.setAttribute(
                            "aria-expanded",
                            "false",
                          );
                        } else {
                          listbox.classList.add("dropdown-active");
                          event.currentTarget.setAttribute(
                            "aria-expanded",
                            "true",
                          );
                        }
                      } else if (event.key === "Escape") {
                        event.currentTarget.nextElementSibling.classList.remove(
                          "dropdown-active",
                        );
                        event.currentTarget.setAttribute(
                          "aria-expanded",
                          "false",
                        );
                      }
                    },
                  },
                  "3 years",
                ),
                ul(
                  {
                    class: "dropdown-list",
                    role: "listbox",
                    id: "returns-period-list",
                    "aria-labelledby": "returns-period-header-label",
                    onclick: (event) => {
                      const option = event.target.closest("li");
                      if (!option) return;
                      // event.target
                      //   .closest(".dropdown-list")
                      //   .classList.remove("dropdown-active");
                      // event.target
                      //   .closest(".return-select-container")
                      //   .querySelector(".selectedtext")
                      //   .setAttribute("aria-expanded", "false");
                      // const name = option.textContent.trim();
                      // event.target
                      //   .closest(".return-select-container")
                      //   .querySelector("p").innerText = "";
                      // event.target
                      //   .closest(".return-select-container")
                      //   .querySelector("p").innerText = name;
                      // dataMapMoObj.selectreturnstemp = name;
                      const listbox = event.target.closest(".dropdown-list");
                      listbox.classList.remove("dropdown-active");

                      const comboTrigger = event.target
                        .closest(".return-select-container")
                        .querySelector(".selectedtext");
                      comboTrigger.setAttribute("aria-expanded", "false");

                      const name = option.textContent.trim();
                      comboTrigger.innerText = name;
                      dataMapMoObj.selectreturnstemp = name;

                      // Manage active selected attributes programmatically
                      listbox
                        .querySelectorAll('[role="option"]')
                        .forEach((opt) => {
                          opt.setAttribute("aria-selected", "false");
                        });
                      option.setAttribute("aria-selected", "true");

                      const keydrop = dataMapMoObj.objtempdrop[name];
                      const sortKey = dataMapMoObj.ObjTemp[keydrop];
                      const targetPlanName = Array.from(
                        block.querySelector(".togglebtn").classList,
                      ).includes("toggle-checked")
                        ? "Regular"
                        : "Direct";

                      const getReturnValue = (fund) => {
                        const planCode = fund?.planList?.find(
                          (plan) => plan.planName === targetPlanName,
                        )?.planCode;
                        const returnObj = fund?.returns?.find(
                          (ret) => ret.plancode === planCode,
                        );
                        const planValue = parseFloat(returnObj?.[sortKey]);
                        if (!Number.isNaN(planValue)) {
                          return planValue;
                        }
                        const fallbackValue = parseFloat(
                          fund?.returns?.[0]?.[sortKey],
                        );
                        return Number.isNaN(fallbackValue)
                          ? -Infinity
                          : fallbackValue;
                      };

                      // 1. Separate the list into two arrays based on the ETF tag
                      const nonETFs = dataMapMoObj.funddata.filter(
                        (f) =>
                          !f.fundsTaggingSection.includes(
                            "motilal-oswal-amc:etf",
                          ),
                      );
                      const ETFs = dataMapMoObj.funddata.filter((f) =>
                        f.fundsTaggingSection.includes("motilal-oswal-amc:etf"),
                      );

                      // 2. Sort only the non-ETF array by return (Descending)
                      nonETFs.sort((a, b) => {
                        const valA = getReturnValue(a);
                        const valB = getReturnValue(b);
                        return valB - valA;
                      });

                      ETFs.sort((a, b) => {
                        const valA = getReturnValue(a);
                        const valB = getReturnValue(b);
                        return valB - valA;
                      });

                      // 4. Combine them: Non-ETFs first, ETFs last
                      let finalResult = [...nonETFs, ...ETFs];
                      const nfofund = finalResult.filter((nfo) => {
                        const funnfo = getFundStatus(nfo);
                        if (
                          !funnfo.isNFO &&
                          nfo.fundsTaggingSection.includes(
                            "motilal-oswal-amc:nfo",
                          )
                        ) {
                          const indexval = nfo.fundsTaggingSection.indexOf(
                            "motilal-oswal-amc:nfo",
                          );
                          nfo.fundsTaggingSection.splice(indexval, 1);
                        }
                        if (
                          funnfo.isNFO &&
                          !funnfo.investEnabled &&
                          nfo.fundsTaggingSection.includes(
                            "motilal-oswal-amc:nfo",
                          )
                        ) {
                          listingData.cfDataObjs =
                            listingData.cfDataObjs.filter(
                              (el, indexval) =>
                                listingData.cfDataObjs.indexOf(nfo) !==
                                indexval,
                            );
                        }
                        return (
                          funnfo.isNFO &&
                          nfo.fundsTaggingSection.includes(
                            "motilal-oswal-amc:nfo",
                          )
                        );
                      });
                      if (nfofund.length !== 0) {
                        const fundstatusv3 = getFundStatus(nfofund[0]);
                        if (
                          nfofund.length !== 0 &&
                          !fundstatusv3.isNFO &&
                          [...nfofund[0].fundsTaggingSection].includes(
                            "motilal-oswal-amc:nfo",
                          )
                        ) {
                          const tags = nfofund[0].fundsTaggingSection.filter(
                            (item) => item !== "motilal-oswal-amc:nfo",
                          );
                          nfofund[0].fundsTaggingSection = tags || [];
                        }
                        finalResult = finalResult.filter((filterel) => {
                          const tags = filterel.fundsTaggingSection;
                          if (!tags) return true; // Keep the item if there are no tags to check
                          return filterel.schcode !== nfofund[0].schcode;
                        });
                        finalResult = appendUniqueFunds(finalResult, nfofund);
                        // }
                      }
                      dataMapMoObj.funddata = finalResult;
                      // const dataattr = event.target
                      //   .getAttribute('dataattr')
                      //   .split('-');
                      // const sorttextcont = block
                      // .querySelector('.sort-select-container .selectedtext');
                      // const sorttext = sorttextcont.textContent.trim();
                      // if (sorttext === 'Popular') {
                      //   dataMapMoObj.funddata = '';
                      //   const popular = listingData.mostBoughtFunds.map((el) => el.split(':')[0]);
                      //   const tempDfilttweelen = listingData.cfDataObjs.filter((el) => {
                      //     if (!popular.includes(el.schemeName)) {
                      //       return false;
                      //     }
                      //     return el;
                      //   });
                      //   dataMapMoObj.funddata = tempDfilttweelen.slice(0, 10);
                      // }
                      // if (sorttext === 'Oldest to Newest') {
                      //   const tempDfilttweelenone = listingData.cfDataObjs
                      //     .filter((el) => {
                      //       if (!el.fundsTaggingSection || !el.planList) {
                      //         return false;
                      //       }
                      //       return el;
                      //     });
                      //   const tempData = JSON.parse(JSON.stringify(tempDfilttweelenone));
                      //   const tempa = tempData.sort(
                      //     (a, b) => new Date(a.dateOfAllotment) - new Date(b.dateOfAllotment),
                      //   );
                      //   dataMapMoObj.funddata = '';
                      //   dataMapMoObj.funddata = tempa;
                      // }
                      // if (sorttext === 'Newest to Oldest') {
                      //   const tempDfilttweefive = listingData.cfDataObjs
                      //     .filter((el) => {
                      //       if (!el.fundsTaggingSection || !el.planList) {
                      //         return false;
                      //       }
                      //       return el;
                      //     });
                      //   const tempData = JSON.parse(JSON.stringify(tempDfilttweefive));
                      //   const tempa = tempData.sort(
                      //     (a, b) => new Date(b.dateOfAllotment) - new Date(a.dateOfAllotment),
                      //   );
                      //   dataMapMoObj.funddata = '';
                      //   dataMapMoObj.funddata = tempa;
                      // }
                      // if (sorttext === 'By Returns') {
                      //   const selectdrop = dataMapMoObj.ObjTemp[dataMapMoObj.objtempdrop[dataMapMoObj.selectreturnstemp]];
                      //   const targetPlanName = Array.from(block.querySelector('.togglebtn').classList).includes('toggle-checked') ? 'Regular' : 'Direct';

                      //   const tempDfiltninteena = listingData.cfDataObjs
                      //     .filter((fund) => {
                      //       // 1. Get the code from planList (Key is 'planCode')
                      //       const planObj = fund.planList?.find((p) => p.planName === targetPlanName);
                      //       const pCode = planObj?.planCode;

                      //       if (!pCode) return false;

                      //       // 2. Find matching return (Key in returns array is 'plancode')
                      //       const returnObj = fund.returns?.find((r) => r.plancode === pCode);
                      //       const val = parseFloat(returnObj?.[selectdrop]);

                      //       // Only show if return exists and is not 0
                      //       return !isNaN(val) && val !== 0;
                      //     })
                      //     .sort((alist, blist) => {
                      //       const getVal = (fund) => {
                      //         const pCode = fund.planList.find((p) => p.planName === targetPlanName)?.planCode;
                      //         const rData = fund.returns.find((r) => r.plancode === pCode);
                      //         return parseFloat(rData?.[selectdrop] || 0);
                      //       };

                      //       return getVal(blist) - getVal(alist); // Descending
                      //     });
                      //   dataMapMoObj.funddata = '';
                      //   dataMapMoObj.funddata = tempDfiltninteena;
                      // }
                      dataMapMoObj.deskrightdrp = name;
                      dataMapMoObj.selectreturns =
                        dataMapMoObj.toTitleCase(name);
                      const searInp = block.querySelector(
                        ".search-input input",
                      );
                      searInp.value = "";
                      const cancelBtn = ensureCancelButton(
                        block.querySelector(".cancel-search"),
                      );
                      cancelBtn.style.display = "none";
                      // const flitwrap = block.querySelector('.applied-filter-wrap');
                      // if (Array.from(flitwrap.classList).includes('filter-active')) {
                      //   flitwrap.classList.remove('filter-active');
                      // }
                      // Array.from(block.querySelector('.filter-list-wrapper').children).forEach((el) => {
                      //   if (el.closest('.checkbox-label-container') !== null && el.closest('.checkbox-label-container')?.querySelector('.innerindianequity')) {
                      //     el.closest('.checkbox-label-container').querySelectorAll('.innerindianequity input').forEach((elemsub) => {
                      //       if (elemsub.checked) {
                      //         elemsub.checked = false;
                      //       }
                      //     });
                      //   }
                      //   if (el.closest('.checkbox-label-container') !== null && el.querySelector('input').checked) {
                      //     // const moplabel = el.querySelector('input').nextElementSibling;
                      //     if (!Array.from(el.querySelector('input').classList).includes('indian-equity')) {
                      //       if (el.querySelector('input').checked) {
                      //         el.querySelector('input').checked = false;
                      //       }
                      //     }
                      //   }
                      // });
                      // block.querySelectorAll('.return-container input').forEach((elre) => {
                      //   const tempret = elre.nextElementSibling.textContent;
                      //   elre.checked = false;
                      //   if (tempret.toLowerCase() === name.toLowerCase()) {
                      //     // elre.click();
                      //     elre.checked = true;
                      //     elre.dispatchEvent(new Event('change', { bubbles: true }));
                      //   }
                      // });
                      viewFunction(block);
                    },
                  },
                  li(
                    {
                      dataattr:
                        dataMapMoObj.data.sort[0].inception_Ret.join("-"),
                      role: "option",
                      "aria-selected": "false",
                      tabindex: "0",
                      "aria-label": "Select Since Inception returns period",
                      onkeydown: (event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.target.click();
                        }
                      },
                    },
                    "Since Inception",
                  ),
                  li(
                    {
                      dataattr: dataMapMoObj.data.sort[0].oneYear_Ret.join("-"),
                      role: "option",
                      "aria-selected": "false",
                      tabindex: "0",
                      "aria-label": "Select 1 year returns period",
                      onkeydown: (event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.target.click();
                        }
                      },
                    },
                    "1 year",
                  ),
                  li(
                    {
                      dataattr:
                        dataMapMoObj.data.sort[0].threeYear_Ret.join("-"),
                      role: "option",
                      "aria-selected": "true",
                      tabindex: "0",
                      "aria-label": "Select 3 years returns period",
                      onkeydown: (event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.target.click();
                        }
                      },
                    },
                    "3 years",
                  ),
                  li(
                    {
                      dataattr:
                        dataMapMoObj.data.sort[0].fiveYear_Ret.join("-"),
                      role: "option",
                      "aria-selected": "false",
                      tabindex: "0",
                      "aria-label": "Select 5 years returns period",
                      onkeydown: (event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.target.click();
                        }
                      },
                    },
                    "5 years",
                  ),
                  li(
                    {
                      dataattr:
                        dataMapMoObj.data.sort[0].sevenYear_Ret.join("-"),
                      role: "option",
                      "aria-selected": "false",
                      tabindex: "0",
                      "aria-label": "Select 7 years returns period",
                      onkeydown: (event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.target.click();
                        }
                      },
                    },
                    "7 years",
                  ),
                  li(
                    {
                      dataattr: dataMapMoObj.data.sort[0].tenYear_Ret.join("-"),
                      role: "option",
                      "aria-selected": "false",
                      tabindex: "0",
                      "aria-label": "Select 10 years returns period",
                      onkeydown: (event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          event.target.click();
                        }
                      },
                    },
                    "10 years",
                  ),
                ),
              ),
            ),
          ),
          div(
            {
              class: "group-view-container",
            },
            div(
              {
                class: "view-container",
                // role: "radiogroup",
                // "aria-label": "View layout switcher",
              },
              fieldset(
                {
                  class: "sr-only",
                },
                legend({ class: "sr-only" }, "View type"),
                label(
                  {
                    class: "sr-only",
                    for: "view-type-grid",
                  },
                  "Grid view",
                ),
                input({
                  id: "view-type-grid",
                  type: "radio",
                  name: "view-type",
                  value: "grid",
                  checked: true,
                  onfocus: () =>
                    block
                      .querySelector(".squareby-container")
                      .classList.add("focus-ring-active"),
                  onblur: () =>
                    block
                      .querySelector(".squareby-container")
                      .classList.remove("focus-ring-active"),
                  // onchange: (event) => {
                  //   const viewContainer =
                  //     event.currentTarget.closest(".view-container");
                  //   const gridButton = viewContainer?.querySelector(
                  //     ".squareby-container",
                  //   );
                  //   if (gridButton) gridButton.click();
                  // },
                  onchange: (event) => {
                    const container =
                      event.currentTarget.closest(".right-container");
                    container.querySelector(".list-view-header").style.display =
                      "none";
                    block
                      .querySelector(".squareby-container")
                      .classList.add("grid-view-active");
                    // block.querySelector(".squareby-container").setAttribute("aria-checked", "true");
                    block
                      .querySelector(".listby-container")
                      .classList.remove("list-view-active");
                    // block.querySelector(".listby-container").setAttribute("aria-checked", "false");
                    viewFunction(block);
                  },
                }),
                label(
                  {
                    class: "sr-only",
                    for: "view-type-list",
                  },
                  "List view",
                ),
                input({
                  id: "view-type-list",
                  type: "radio",
                  name: "view-type",
                  value: "list",
                  // onchange: (event) => {
                  //   const viewContainer =
                  //     event.currentTarget.closest(".view-container");
                  //   const listButton =
                  //     viewContainer?.querySelector(".listby-container");
                  //   if (listButton) listButton.click();
                  // },
                  onfocus: () =>
                    block
                      .querySelector(".listby-container")
                      .classList.add("focus-ring-active"),
                  onblur: () =>
                    block
                      .querySelector(".listby-container")
                      .classList.remove("focus-ring-active"),
                  onchange: (event) => {
                    const container =
                      event.currentTarget.closest(".right-container");
                    container.querySelector(".list-view-header").style.display =
                      "block";
                    block
                      .querySelector(".listby-container")
                      .classList.add("list-view-active");
                    // block.querySelector(".listby-container").setAttribute("aria-checked", "true");
                    block
                      .querySelector(".squareby-container")
                      .classList.remove("grid-view-active");
                    // block.querySelector(".squareby-container").setAttribute("aria-checked", "false");
                    viewFunction(block);
                  },
                }),
              ),
              div(
                {
                  class: "squareby-container grid-view-active",
                  // role: "button",
                  // tabindex: "0",
                  // "aria-label": "Grid view",
                  // "aria-pressed": "true",
                  // "aria-hidden": "true",
                  // role: "radio",
                  // "aria-checked": "true",
                  // "aria-label": "Grid view",
                  // tabindex: "-1",
                  onclick: (event) => {
                    // const viewContainer =
                    //   event.currentTarget.closest(".view-container");
                    // const gridRadio = viewContainer?.querySelector(
                    //   'input[name="view-type"][value="grid"]',
                    // );
                    // if (gridRadio) gridRadio.checked = true;
                    // event.currentTarget.classList.add("grid-view-active");
                    // event.currentTarget
                    //   .closest(".view-container")
                    //   .querySelector(".listby-container")
                    //   .classList.remove("list-view-active");
                    // event.currentTarget
                    //   .closest(".right-container")
                    //   .querySelector(".list-view-header").style.display =
                    //   "none";

                    const nativeRadio = event.currentTarget
                      .closest(".view-container")
                      ?.querySelector("#view-type-grid");

                    if (nativeRadio && !nativeRadio.checked) {
                      nativeRadio.checked = true;
                      // Fire a single event that bubbles down to trigger the main viewFunction()
                      nativeRadio.dispatchEvent(
                        new Event("change", { bubbles: true }),
                      );
                    }

                    // Update ARIA states
                    // event.currentTarget.setAttribute("aria-checked", "true");
                    // event.currentTarget
                    //   .closest(".view-container")
                    //   .querySelector(".listby-container")
                    //   .setAttribute("aria-checked", "false");

                    if (
                      block.querySelector(".search-input .search").value !== ""
                    ) {
                      const searchval = block.querySelector(
                        ".search-input .search",
                      ).value;
                      const tempDfilttweentwo = listingData.cfDataObjs.filter(
                        (el) => {
                          if (!el.fundsTaggingSection || !el.planList) {
                            return false;
                          }
                          return el;
                        },
                      );
                      dataMapMoObj.funddata = tempDfilttweentwo.filter(
                        (ellim) => ellim.schemeName === searchval,
                      );
                    }
                    const nfofund = listingData.cfDataObjs.filter((nfo) => {
                      const funnfo = getFundStatus(nfo);
                      if (
                        !funnfo.isNFO &&
                        nfo.fundsTaggingSection.includes(
                          "motilal-oswal-amc:nfo",
                        )
                      ) {
                        const indexval = nfo.fundsTaggingSection.indexOf(
                          "motilal-oswal-amc:nfo",
                        );
                        nfo.fundsTaggingSection.splice(indexval, 1);
                      }
                      if (
                        funnfo.isNFO &&
                        !funnfo.investEnabled &&
                        nfo.fundsTaggingSection.includes(
                          "motilal-oswal-amc:nfo",
                        )
                      ) {
                        listingData.cfDataObjs = listingData.cfDataObjs.filter(
                          (el, indexval) =>
                            listingData.cfDataObjs.indexOf(nfo) !== indexval,
                        );
                      }
                      return (
                        funnfo.isNFO &&
                        nfo.fundsTaggingSection.includes(
                          "motilal-oswal-amc:nfo",
                        )
                      );
                    });
                    if (nfofund.length !== 0) {
                      const fundstatusv3 = getFundStatus(nfofund[0]);
                      if (
                        nfofund.length !== 0 &&
                        !fundstatusv3.isNFO &&
                        [...nfofund[0].fundsTaggingSection].includes(
                          "motilal-oswal-amc:nfo",
                        )
                      ) {
                        const tags = nfofund[0].fundsTaggingSection.filter(
                          (item) => item !== "motilal-oswal-amc:nfo",
                        );
                        nfofund[0].fundsTaggingSection = tags || [];
                      }
                      dataMapMoObj.funddata = dataMapMoObj.funddata.filter(
                        (filterel) => {
                          const tags = filterel.fundsTaggingSection;
                          if (!tags) return true; // Keep the item if there are no tags to check
                          return filterel.schcode !== nfofund[0].schcode;
                        },
                      );
                      dataMapMoObj.funddata = appendUniqueFunds(
                        dataMapMoObj.funddata,
                        nfofund,
                      );
                      // }
                    }
                    viewFunction(block);
                  },
                  onkeydown: (event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      event.currentTarget.click();
                    }
                  },
                },
                block.querySelector(".block-item3 .block-subitem-finelsub4"),
              ),
              div(
                {
                  class: "listby-container",
                  // role: "button",
                  // tabindex: "0",
                  // "aria-label": "List view",
                  // "aria-pressed": "false",
                  // "aria-hidden": "true",
                  // role: "radio",
                  // "aria-checked": "false",
                  // tabindex: "-1", // Keeps it out of keyboard tab streams to avoid double focus
                  // "aria-label": "List view",
                  onclick: (event) => {
                    // const viewContainer =
                    //   event.currentTarget.closest(".view-container");
                    // const listRadio = viewContainer?.querySelector(
                    //   'input[name="view-type"][value="list"]',
                    // );
                    // if (listRadio) listRadio.checked = true;
                    // event.currentTarget.classList.add("list-view-active");
                    // event.currentTarget
                    //   .closest(".view-container")
                    //   .querySelector(".squareby-container")
                    //   .classList.remove("grid-view-active");
                    // event.currentTarget
                    //   .closest(".right-container")
                    //   .querySelector(".list-view-header").style.display =
                    //   "block";

                    const nativeRadio = event.currentTarget
                      .closest(".view-container")
                      ?.querySelector("#view-type-list");

                    if (nativeRadio && !nativeRadio.checked) {
                      nativeRadio.checked = true;
                      // Fire a single event that bubbles down to trigger the main viewFunction()
                      nativeRadio.dispatchEvent(
                        new Event("change", { bubbles: true }),
                      );
                    }

                    // Update ARIA states
                    // event.currentTarget.setAttribute("aria-checked", "true");
                    // event.currentTarget
                    //   .closest(".view-container")
                    //   .querySelector(".squareby-container")
                    //   .setAttribute("aria-checked", "false");

                    if (
                      block.querySelector(".search-input .search").value !== ""
                    ) {
                      const searchval = block.querySelector(
                        ".search-input .search",
                      ).value;
                      const tempDfilttweethree = listingData.cfDataObjs.filter(
                        (el) => {
                          if (!el.fundsTaggingSection || !el.planList) {
                            return false;
                          }
                          return el;
                        },
                      );
                      dataMapMoObj.funddata = tempDfilttweethree.filter(
                        (ellim) => ellim.schemeName === searchval,
                      );
                    }
                    const nfofund = listingData.cfDataObjs.filter((nfo) => {
                      const funnfo = getFundStatus(nfo);
                      if (
                        !funnfo.isNFO &&
                        nfo.fundsTaggingSection.includes(
                          "motilal-oswal-amc:nfo",
                        )
                      ) {
                        const indexval = nfo.fundsTaggingSection.indexOf(
                          "motilal-oswal-amc:nfo",
                        );
                        nfo.fundsTaggingSection.splice(indexval, 1);
                      }
                      if (
                        funnfo.isNFO &&
                        !funnfo.investEnabled &&
                        nfo.fundsTaggingSection.includes(
                          "motilal-oswal-amc:nfo",
                        )
                      ) {
                        listingData.cfDataObjs = listingData.cfDataObjs.filter(
                          (el, indexval) =>
                            listingData.cfDataObjs.indexOf(nfo) !== indexval,
                        );
                      }
                      return (
                        funnfo.isNFO &&
                        nfo.fundsTaggingSection.includes(
                          "motilal-oswal-amc:nfo",
                        )
                      );
                    });
                    if (nfofund.length !== 0) {
                      const fundstatus = getFundStatus(nfofund[0]);
                      if (
                        nfofund.length !== 0 &&
                        !fundstatus.isNFO &&
                        [...nfofund[0].fundsTaggingSection].includes(
                          "motilal-oswal-amc:nfo",
                        )
                      ) {
                        const tags = nfofund[0].fundsTaggingSection.filter(
                          (item) => item !== "motilal-oswal-amc:nfo",
                        );
                        nfofund[0].fundsTaggingSection = tags || [];
                      }
                      // if (shouldShowCard(nfofund)) {
                      dataMapMoObj.funddata = dataMapMoObj.funddata.filter(
                        (filterel) => {
                          const tags = filterel.fundsTaggingSection;
                          if (!tags) return true; // Keep the item if there are no tags to check
                          return filterel.schcode !== nfofund[0].schcode;
                        },
                      );
                      dataMapMoObj.funddata = appendUniqueFunds(
                        dataMapMoObj.funddata,
                        nfofund,
                      );
                      // }
                    }
                    viewFunction(block);
                  },
                  onkeydown: (event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      event.currentTarget.click();
                    }
                  },
                },
                block.querySelector(".block-item3 .block-subitem-finelsub5"),
              ),
            ),
            div(
              {
                class: "togglebtn",
              },
              p(
                {
                  class: "toggle-text",
                },
                "Direct",
              ),
              div(
                {
                  class: "fund-toggle-wrap",
                },
                input({
                  type: "checkbox",
                  id: "toggle",
                  "aria-label": "Switch between Direct and Regular mode",
                  onchange: (event) => {
                    if (event.target.checked) {
                      event.target
                        .closest(".togglebtn")
                        .classList.add("toggle-checked");
                      showRegularPlanPopover();
                    } else {
                      event.target
                        .closest(".togglebtn")
                        .classList.remove("toggle-checked");
                    }
                    // event.target.checked
                    // viewFunction(block);
                    checkfilter(block);
                  },
                  onkeydown: (event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      event.target.checked = !event.target.checked;
                      event.target.dispatchEvent(
                        new Event("change", { bubbles: true }),
                      );
                    }
                  },
                }),
                label(
                  {
                    class: "fund-toggle",
                    for: "toggle",
                  },
                  // Add spans for the visible text inside the label
                  span({ class: "label-text direct" }, "Direct"),
                  span({ class: "label-text regular" }, "Regular"),
                ),
              ),
              p(
                {
                  class: "toggle-text",
                },
                "Regular",
              ),
            ),
            div(
              {
                class: "compare-btn",
              },
              button("Compare"),
            ),
          ),
        ),
        div(
          {
            class: "applied-filter-wrap",
          },
          ul(
            {
              class: "applied-filter-list",
            },
            li(
              {
                class: "applied-filter-name",
              },
              span("Large Cap"),
              img({
                class: "filter-cross-icon",
                src: "/icons/cross-icon.svg",
                alt: "cross icon",
              }),
            ),
            li(
              {
                class: "applied-filter-name",
              },
              span("Tax saver (ELSS)"),
              img({
                src: "/icons/cross-icon.svg",
                alt: "cross icon",
              }),
            ),
            li(
              {
                class: "applied-filter-name",
              },
              span("Hybrid & Balanced"),
              img({
                src: "/icons/cross-icon.svg",
                alt: "cross icon",
              }),
            ),
          ),
        ),
        div(
          {
            class: "cards-container",
          },
          ...dataMapMoObj.funddata.map((el) => fundcardblock(el)),
        ),
        div(
          {
            class: "list-view-header",
            style: "display:none",
          },
          div(
            {
              class: "list-header",
            },
            block.closest(".section").querySelector(".item2"),
          ),
          div({
            class: "list-container",
          }),
        ),
      ),
    ),
  );
  block.innerHTML = "";
  block.append(divfund);
  block.querySelectorAll(".viewlist-btn img").forEach((imgEl) => {
    imgEl.setAttribute("alt", "");
  });
  block.querySelector(".applied-filter-list").innerHTML = "";
  [...block.querySelectorAll(".sort-container .dropdown-list")].forEach(
    (el) => {
      el.addEventListener("click", (event) => {
        if (event.target.textContent.trim() === "Oldest to Newest") {
          const tempDfilttweeeight = dataMapMoObj.funddata.filter((elemen) => {
            if (!elemen.fundsTaggingSection || !elemen.planList) {
              return false;
            }
            return elemen;
          });
          const tempdata = JSON.parse(JSON.stringify(tempDfilttweeeight));
          const tempa = tempdata.sort(
            (a, b) => new Date(a.dateOfAllotment) - new Date(b.dateOfAllotment),
          );
          dataMapMoObj.funddata = tempa;
        }
        if (event.target.textContent.trim() === "Newest to Oldest") {
          const tempDfilttweenine = dataMapMoObj.funddata.filter((elni) => {
            if (!elni.fundsTaggingSection || !elni.planList) {
              return false;
            }
            return elni;
          });
          const tempdata = JSON.parse(JSON.stringify(tempDfilttweenine));
          const tempa = tempdata.sort(
            (a, b) => new Date(b.dateOfAllotment) - new Date(a.dateOfAllotment),
          );
          dataMapMoObj.funddata = tempa;
        }
        viewFunction(block);
      });
    },
  );
  // Mobile Sorting
  dataMapMoObj.flagsort = "";
  [...block.querySelectorAll(".arrange-container .radio-label")].forEach(
    (mobel) => {
      mobel.addEventListener("click", (event) => {
        const sortText = event.target
          .closest(".radio-label")
          .querySelector("label").textContent;
        if (!Array.isArray(dataMapMoObj.funddata) || dataMapMoObj.funddata.length === 0) {
          dataMapMoObj.funddata = listingData.cfDataObjs.filter(
            (fund) => fund?.fundsTaggingSection && fund?.planList,
          );
        }
        if (sortText.trim() === "Oldest to Newest") {
          const tempDfilthirdyt = dataMapMoObj.funddata.filter((el) => {
            if (!el.fundsTaggingSection || !el.planList) {
              return false;
            }
            return el;
          });
          const tempdata = JSON.parse(JSON.stringify(tempDfilthirdyt));
          const tempa = tempdata.sort(
            (a, b) => new Date(a.dateOfAllotment) - new Date(b.dateOfAllotment),
          );
          dataMapMoObj.funddata = tempa;
        }
        if (sortText.trim() === "Newest to Oldest") {
          const tempDfiltthirdone = dataMapMoObj.funddata.filter((el) => {
            if (!el.fundsTaggingSection || !el.planList) {
              return false;
            }
            return el;
          });
          const tempdata = JSON.parse(JSON.stringify(tempDfiltthirdone));
          const tempa = tempdata.sort(
            (a, b) => new Date(b.dateOfAllotment) - new Date(a.dateOfAllotment),
          );
          dataMapMoObj.funddata = tempa;
        }
        if (sortText.trim() === "Popular") {
          const popular = listingData.mostBoughtFunds.map(
            (el) => el.split(":")[0],
          );
          const tempDfiltthirdtwo = listingData.cfDataObjs.filter((el) => {
            if (!popular.includes(el.schemeName)) {
              return false;
            }
            return el;
          });
          dataMapMoObj.funddata = tempDfiltthirdtwo.slice(0, 10);
        }
        if (sortText.trim() === "By Returns") {
          const selectdrop =
            dataMapMoObj.ObjTemp[
            dataMapMoObj.objtempdrop[dataMapMoObj.selectreturnstemp]
            ];
          const targetPlanName = Array.from(
            block.querySelector(".togglebtn").classList,
          ).includes("toggle-checked")
            ? "Regular"
            : "Direct";

          const tempDfiltninteen = dataMapMoObj.funddata
            .filter((fund) => fund?.planList?.length)
            .sort((alist, blist) => {
              return (
                getBestAvailableReturn(blist, targetPlanName, selectdrop) -
                getBestAvailableReturn(alist, targetPlanName, selectdrop)
              );
            });
          const nfofund = listingData.cfDataObjs.filter((nfo) =>
            nfo.fundsTaggingSection.includes("motilal-oswal-amc:nfo"),
          );
          const fundstatus = getFundStatus(nfofund[0]);
          if (
            nfofund.length !== 0 &&
            !fundstatus.isNFO &&
            [...nfofund[0].fundsTaggingSection].includes(
              "motilal-oswal-amc:nfo",
            )
          ) {
            const tags = nfofund[0].fundsTaggingSection.filter(
              (item) => item !== "motilal-oswal-amc:nfo",
            );
            nfofund[0].fundsTaggingSection = tags || [];
          }
          if (nfofund.length !== 0) {
            dataMapMoObj.funddata = dataMapMoObj.funddata.filter((filterel) => {
              const tags = filterel.fundsTaggingSection;
              if (!tags) return true; // Keep the item if there are no tags to check
              return filterel.schcode !== nfofund[0].schcode;
            });
            // if (shouldShowCard(nfofund)) {
            tempDfiltninteen = appendUniqueFunds(tempDfiltninteen, nfofund);
            // }
          }
          const tempa = JSON.parse(JSON.stringify(tempDfiltninteen));
          dataMapMoObj.funddata = tempa;
        }
        dataMapMoObj.schmenmob = sortText;
        dataMapMoObj.flagsort = "Y";
        viewFunction(block);
      });
    },
  );

  // added wrapper
  const divmop = div(
    {
      class: "indanequity-wrapper",
    },
    block.querySelector(".indian-equity"),
    div(
      {
        class: "label-tooltip-wrap",
      },
      block.querySelector(".label-tooltip-wrap .indian-equity"),
      div(
        {
          class: "tooltip-wrap",
        },
        button(
          {
            class: "filter-info-btn",
            type: "button",
            "aria-describedby": "tooltip-indian-equity",
          },
          img({
            class: "filter-info-icon",
            src: "/icons/filter-info.svg",
            alt: "Filter Info Icon",
          }),
        ),
        div(
          {
            class: "tooltip-text",
            id: "tooltip-indian-equity",
            role: "tooltip",
            style: "display:none",
          },
          "Shares of companies listed on Indian stock exchanges, representing ownership in businesses operating in India.",
        ),
      ),
    ),
  );
  const divinner = block.querySelector(".indaneqsub .innerindianequity");
  block.querySelector(".indaneqsub").innerHTML = "";
  if (divinner !== null) {
    block.querySelector(".indaneqsub").append(divmop, divinner);
  } else {
    block.querySelector(".indaneqsub").append(divmop);
  }

  searchFunctionality(block);
  Array.from(
    block.querySelector(".return-container .radio-label-container").children,
  ).forEach((el) => {
    el.querySelector("input").addEventListener("click", (event) => {
      // const dataattr = event.target.getAttribute('dataattr').split('-');
      const tempDfiltthirdfour = listingData.cfDataObjs.filter((elfou) => {
        if (!elfou.fundsTaggingSection || !elfou.planList) {
          return false;
        }
        return elfou;
      });
      const tempdata = tempDfiltthirdfour;
      // .filter((elem) => dataattr.includes(elem.schcode));
      // 1. Select the checked radio button specifically inside .arrange-container
      const checkedInput = document.querySelector(
        '.arrange-container input[type="radio"]:checked',
      );
      let selectedText;
      let tempdataArr;
      if (checkedInput) {
        selectedText = checkedInput.nextElementSibling.textContent;
      }

      if (selectedText === "Oldest to Newest") {
        tempdataArr = tempdata.sort(
          (a, b) => new Date(a.dateOfAllotment) - new Date(b.dateOfAllotment),
        );
        // dataMapMoObj.tempMobReturn = tempa;
      }
      if (selectedText === "Newest to Oldest") {
        tempdataArr = tempdata.sort(
          (a, b) => new Date(b.dateOfAllotment) - new Date(a.dateOfAllotment),
        );
        // dataMapMoObj.tempMobReturn = tempa;
      }
      if (selectedText === "Popular") {
        const popular = listingData.mostBoughtFunds.map(
          (elpopular) => elpopular.split(":")[0],
        );
        tempdataArr = tempdata
          .filter((fund) => popular.includes(fund.schemeName))
          .sort(
            (a, b) =>
              popular.indexOf(a.schemeName) - popular.indexOf(b.schemeName),
          );
      }

      const selectedPeriod =
        event.target.nextElementSibling?.textContent?.trim() || "3 years";
      dataMapMoObj.selectreturnstemp = selectedPeriod;

      if (selectedText === "By Returns") {
        const keydrop = dataMapMoObj.objtempdrop[selectedPeriod];
        const sortKey = dataMapMoObj.ObjTemp[keydrop];
        const targetPlanName = Array.from(
          block.querySelector(".togglebtn").classList,
        ).includes("toggle-checked")
          ? "Regular"
          : "Direct";

        const getReturnValue = (fund) => {
          return getBestAvailableReturn(fund, targetPlanName, sortKey);
        };

        const nonETFs = tempdata.filter(
          (fund) => !fund.fundsTaggingSection.includes("motilal-oswal-amc:etf"),
        );
        const ETFs = tempdata.filter((fund) =>
          fund.fundsTaggingSection.includes("motilal-oswal-amc:etf"),
        );

        nonETFs.sort((a, b) => getReturnValue(b) - getReturnValue(a));
        ETFs.sort((a, b) => getReturnValue(b) - getReturnValue(a));
        tempdataArr = [...nonETFs, ...ETFs];
      }

      dataMapMoObj.tempMobReturn = [];
      dataMapMoObj.tempMobReturn = tempdataArr || tempdata;
      // viewFunction(block);
    });
  });
  block.querySelectorAll(".arrange-container input")[0].click();
  block.querySelectorAll(".return-container input")[2].click();
  if (!dataMapMoObj.selectreturnstemp) {
    dataMapMoObj.selectreturnstemp = "3 years";
  }
  if (!dataMapMoObj.selectreturns) {
    dataMapMoObj.selectreturns = "3 Years";
  }
  if (!dataMapMoObj.deskrightdrp) {
    dataMapMoObj.deskrightdrp = "3 Years";
  }
  // Apply default period/sort ordering to cards on first load.
  viewFunction(block);
  Array.from(block.querySelectorAll(".filter-list-wrapper input")).forEach(
    (el) => {
      if (
        el.getAttribute("datakey") !== null &&
        checkboxSel === el.getAttribute("datakey")
      ) {
        if (checkboxSel === "indian-equity") {
          el.checked = true;
          block
            .querySelectorAll(".indian-equity-container input")
            .forEach((inner) => {
              inner.checked = true;
            });
        } else {
          el.checked = true;
        }
      }
    },
  );

  const applyMobileFiltersOnLoad = () => {
    if (window.innerWidth >= 786) {
      return;
    }

    const checkedFilters = Array.from(
      block.querySelectorAll(
        '.filter-list-wrapper .checkbox-label-container input[type="checkbox"]:checked',
      ),
    );
    if (checkedFilters.length === 0) {
      return;
    }

    const selectedCodes = [];
    checkedFilters.forEach((el) => {
      const dataAttr = el.getAttribute("dataattr") || "";
      if (dataAttr) {
        selectedCodes.push(...dataAttr.split("-"));
      }
    });

    const uniqueSelectedCodes = [
      ...new Set(selectedCodes.map((code) => String(code).trim())),
    ].filter(Boolean);
    if (uniqueSelectedCodes.length === 0) {
      return;
    }

    const tempDfiltOnload = listingData.cfDataObjs.filter((el) => {
      if (!el.fundsTaggingSection || !el.planList) {
        return false;
      }
      return uniqueSelectedCodes.includes(String(el.schcode));
    });

    dataMapMoObj.tempMobReturn = tempDfiltOnload;
    applyFunction(block, { forceMobileApply: true });
  };

  const showTooltip = (btn) => {
    const wrapper = btn?.closest(".tooltip-wrap");
    if (wrapper?.classList.contains("tooltip-dismissed")) return;
    const tooltip = wrapper?.querySelector(".tooltip-text");
    if (tooltip) tooltip.style.display = "block";
  };

  const hideTooltip = (btn) => {
    const tooltip = btn
      ?.closest(".tooltip-wrap")
      ?.querySelector(".tooltip-text");
    if (tooltip) tooltip.style.display = "none";
  };

  const hideAllTooltips = ({ dismiss = false } = {}) => {
    Array.from(block.querySelectorAll(".tooltip-wrap")).forEach((wrap) => {
      const tip = wrap.querySelector(".tooltip-text");
      if (tip) tip.style.display = "none";
      if (dismiss) wrap.classList.add("tooltip-dismissed");
    });
  };

  const clearTooltipDismissed = (btn) => {
    const wrapper = btn?.closest(".tooltip-wrap");
    if (wrapper) wrapper.classList.remove("tooltip-dismissed");
  };

  const isWithinTooltipWrap = (target, btn) => {
    const wrapper = btn?.closest(".tooltip-wrap");
    return !!(wrapper && target && wrapper.contains(target));
  };

  const tooltipButtons = block.querySelectorAll(".filter-info-btn");
  tooltipButtons.forEach((btn) => {
    const tooltip = btn
      .closest(".tooltip-wrap")
      ?.querySelector(".tooltip-text");
    const handleTooltipEscape = (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        hideAllTooltips({ dismiss: true });
        btn.focus();
      }
    };
    // if (tooltip && !tooltip.hasAttribute("tabindex")) {
    //   tooltip.setAttribute("tabindex", "0");
    // }

    btn.addEventListener("focus", () => {
      clearTooltipDismissed(btn);
      showTooltip(btn);
    });
    btn.addEventListener("blur", (event) => {
      if (!isWithinTooltipWrap(event.relatedTarget, btn)) {
        hideTooltip(btn);
      }
      clearTooltipDismissed(btn);
    });
    btn.addEventListener("mouseenter", () => {
      clearTooltipDismissed(btn);
      showTooltip(btn);
    });
    btn.addEventListener("mouseleave", (event) => {
      if (!isWithinTooltipWrap(event.relatedTarget, btn)) {
        hideTooltip(btn);
      }
      clearTooltipDismissed(btn);
    });
    btn.addEventListener("click", (event) => {
      event.stopPropagation();
      clearTooltipDismissed(btn);
      const tooltip = btn
        .closest(".tooltip-wrap")
        ?.querySelector(".tooltip-text");
      if (tooltip) {
        const isOpen = tooltip.style.display === "block";
        hideAllTooltips();
        tooltip.style.display = isOpen ? "none" : "block";
      }
    });
    btn.addEventListener("keydown", handleTooltipEscape);

    if (tooltip) {
      tooltip.addEventListener("mouseenter", () => {
        clearTooltipDismissed(btn);
        showTooltip(btn);
      });
      tooltip.addEventListener("mouseleave", () => {
        hideTooltip(btn);
      });
      // tooltip.addEventListener("focus", () => {
      //   clearTooltipDismissed(btn);
      //   showTooltip(btn);
      // });
      // tooltip.addEventListener("blur", () => {
      //   hideTooltip(btn);
      // });
      tooltip.addEventListener("keydown", handleTooltipEscape);
    }
  });

  document.addEventListener("click", (event) => {
    try {
      if (
        !block.querySelector(".sort-select-container").contains(event.target)
      ) {
        const sortcont = block.querySelector(
          ".sort-select-container .dropdown-list",
        );
        sortcont.classList.remove("dropdown-active");
      }
      if (
        !block.querySelector(".return-select-container").contains(event.target)
      ) {
        const sortcont = block.querySelector(
          ".return-select-container .dropdown-list",
        );
        sortcont.classList.remove("dropdown-active");
      }
      if (!event.target.closest(".tooltip-wrap")) {
        hideAllTooltips();
      }
    } catch (error) {
      // console.log(error);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      hideAllTooltips({ dismiss: true });
    }
  });

  if (block.closest(".fund-listing-variant-two")) {
    block.querySelector("#fundtype2").click();
    block.querySelector("#fundtype3").parentElement.style.display = "none";
    Array.from(document.querySelectorAll(".checkbox-label-container")).forEach(
      (container) => {
        let plancode = "";
        let count = 0;
        const datattr = container
          .querySelector("input")
          .getAttribute("dataattr")
          .split("-");
        listingData.cfDataObjs.forEach((cfdata) => {
          if (
            datattr.includes(cfdata.schcode) &&
            cfdata.fundsTaggingSection.includes("motilal-oswal-amc:index-funds")
          ) {
            plancode = "Y";
            count += 1;
          }
        });
        if (plancode === "Y") {
          container.querySelector(".fund-length").innerText = "";
          container.querySelector(".fund-length").innerText = `(${count})`;
        }
        if (plancode === "") {
          container.style.display = "none";
        }
      },
    );
  }

  // Set initial clearall button state based on filters
  updateClearallButtonState(block);
  if (checkboxSel !== "") {
    const nfoevent = document.querySelector(".nfo");
    checkfilter(block);
    if (window.getComputedStyle(nfoevent).display !== "none") {
      nfoevent.click();
    }
  }
  applyMobileFiltersOnLoad();

  if (typeof dataMapMoObj.syncCategoryRadioGroups === "function") {
    dataMapMoObj.syncCategoryRadioGroups();
  }

  // --- ACCESSIBILITY FOCUS OUT DROPDOWN SYSTEM ---
  const handleDropdownFocusOut = (containerSelector) => {
    const container = block.querySelector(containerSelector);
    if (!container) return;

    const trigger = container.querySelector(".selectedtext");
    const dropdownList = container.querySelector(".dropdown-list");

    container.addEventListener("focusout", (event) => {
      // requestAnimationFrame guarantees the browser completes updating document.activeElement
      requestAnimationFrame(() => {
        if (!container.contains(document.activeElement)) {
          dropdownList.classList.remove("dropdown-active");
          trigger.setAttribute("aria-expanded", "false");
        }
      });
    });
  };

  // Monitor both sorting and returns period dropdown UI systems
  handleDropdownFocusOut(".sort-select-container");
  handleDropdownFocusOut(".return-select-container");
  return block;
}

// Navter Fund Decorate star

dataMapMoObj.param = {
  category: "",
  sort: "",
  month: "",
  year: "",
  search: "",
  type: "",
};

dataMapMoObj.downloadCode = (block) => {
  const valAry = ["internationalbusiness", "mf", "pms", "aif"];
  const classList = Array.from(block.closest(".section").classList);
  const matchedClass = classList.find((className) =>
    valAry.includes(className),
  );
  if (matchedClass) {
    // const index = valAry.indexOf(matchedClass);
    // console.log('Matched Class:', matchedClass);
    dataMapMoObj.param.type = matchedClass;
    // console.log('Index in valAry:', index);
  }
  dataMapMoObj.CLASS_PREFIXES = ["block-item"];
  dataMapMoObj.addIndexed(block);
  const placehold = block
    .querySelector(".block-item1 p:nth-child(2)")
    .cloneNode(true);
  const headtitle = block
    .querySelector(".block-item1 > div > h1")
    .cloneNode(true);
  const leftsubtitle = block.querySelector(".block-item2 p").cloneNode(true);
  const leftside = block.querySelector(".block-item2 ul");
  const downloadtext = block.querySelector(
    ".block-item3 p:nth-child(1)",
  ).textContent;
  const downloadicon = block.querySelector(".block-item3 .icon-xlsx-icon img");
  const errorscrren = block
    .querySelector(".block-item3 p:nth-child(2)")
    .cloneNode(true);
  const searchnodoc = block
    .querySelector(".block-item3 p:nth-child(3)")
    .cloneNode(true);
  const searchfour = block.querySelector(".block-item3 p:nth-child(4)");
  const blockwrapper = div(
    { class: "download-container" },
    div(
      { class: "search-container" },
      div({ class: "download-title-wrap" }, headtitle),
      div(
        { class: "search-filter-wrap" },
        div(
          { class: "search-mainbox" },
          div(
            { class: "search-wrapper" },
            input({
              class: "search-inp",
              id: "search-field",
              placeholder: placehold.textContent,
              "aria-label": placehold.textContent,
              "aria-describedby": "search-field-hint search-field-status",
              "aria-expanded": "false",
              "aria-controls": "search-suggestions-list",
              autocomplete: "off",
            }),
            span(
              { class: "sr-only", id: "search-field-hint" },
              "Suggestions will appear as you start typing. Use the arrow keys to browse them.",
            ),
            // label(
            // {
            // for: 'search-field',
            // class: 'search-label',
            // },
            // searchPlaceholder.trim(),
            // ),
            button(
              {
                class: "cancel-search",
                type: "button",
                "aria-label": "clear",
              },
              img({
                class: "cancel-btn",
                src: "/icons/input-cancel.svg",
                alt: "clear",
                fetchpriority: "high",
                loading: "eager",
              }),
            ),
            span(
              { class: "sr-only", id: "search-field-status", role: "status" },
              "",
            ),
            div(
              { class: "docs-searchlist" },
              div(
                { class: "searchlist-wrap" },
                ul(
                  { class: "docs-list-wrap", id: "search-suggestions-list" },
                  li(
                    { class: "docs-list" },
                    div(
                      { class: "docs-content" },
                      div(
                        { class: "docs-title" },
                        a(
                          { class: "docs-name", href: "#" },
                          "Motilal Oswal BSE Select IPO ETF",
                        ),
                      ),
                      div(
                        { class: "docs-desc" },
                        span({ class: "search-date-ctgry" }, "13 Nov 2025 "),
                        span(
                          { class: "search-date-ctgry" },
                          "Scheme Documents / SID",
                        ),
                      ),
                    ),
                    div(
                      { class: "docs-icon" },
                      a(
                        { class: "docs-file", href: "#" },
                        img({
                          class: "docs-img",
                          src: "../../icons/pdf-icon.svg",
                        }),
                      ),
                    ),
                  ),
                ),
                div(
                  { class: "search-count-desc" },
                  p({ class: "count-desc" }, ""),
                ),
              ),
            ),
          ),
        ),
        div(
          { class: "ctgry-filter-drpdwn" },
          input({
            class: "ctgry-filter-inp",
            id: "ctgry-filter",
            readonly: "",
          }),
          label(
            { class: "ctgry-filter-label", for: "ctgry-filter" },
            "Categories",
          ),
        ),
        div(
          { class: "upper-filter risk-return-activ" },
          div(
            { class: "month-year-wrap" },
            div(
              { class: "smy-drpdwn-wrap cmmn-drpdwn-wrap" },
              span(
                { class: "smy-txt-label drpdwn-label", id: "sort-label" },
                "Sort:",
              ),
              div(
                { class: "smy-select-drpdwn cmmn-select-drpdwn" },
                button(
                  {
                    class: "smy-drpdwn-sltxt drpdwn-sltxt",
                    type: "button",
                    "aria-labelledby": "sort-label",
                    "aria-haspopup": "listbox",
                    "aria-expanded": "false",
                  },
                  span({ class: "selected-txt" }, "Latest"),
                ),
                div(
                  { class: "smy-drpdwn-menu drpdwn-wrap" },
                  div(
                    { class: "drpdwn-menu", role: "listbox", "aria-labelledby": "sort-label" },
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "Latest",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "Oldest to Newest",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "Newest to Oldest",
                    ),
                  ),
                ),
              ),
            ),
            div(
              { class: "smy-drpdwn-wrap cmmn-drpdwn-wrap" },
              span(
                { class: "smy-txt-label drpdwn-label", id: "month-label" },
                "Month",
              ),
              div(
                { class: "smy-select-drpdwn cmmn-select-drpdwn" },
                button(
                  {
                    class: "smy-drpdwn-sltxt drpdwn-sltxt",
                    type: "button",
                    "aria-labelledby": "month-label",
                    "aria-haspopup": "listbox",
                    "aria-expanded": "false",
                  },
                  span({ class: "selected-txt" }, ""),
                ),
                div(
                  { class: "smy-drpdwn-menu drpdwn-wrap" },
                  div(
                    { class: "drpdwn-menu", role: "listbox", "aria-labelledby": "month-label" },
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                  ),
                ),
              ),
            ),
            div(
              { class: "smy-drpdwn-wrap cmmn-drpdwn-wrap" },
              span(
                { class: "smy-txt-label drpdwn-label", id: "year-label" },
                "Year",
              ),
              div(
                { class: "smy-select-drpdwn cmmn-select-drpdwn" },
                button(
                  {
                    class: "smy-drpdwn-sltxt drpdwn-sltxt",
                    type: "button",
                    "aria-labelledby": "year-label",
                    "aria-haspopup": "listbox",
                    "aria-expanded": "false",
                  },
                  span({ class: "selected-txt" }, ""),
                ),
                div(
                  { class: "smy-drpdwn-menu drpdwn-wrap" },
                  div(
                    { class: "drpdwn-menu", role: "listbox", "aria-labelledby": "year-label" },
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                    button(
                      { class: "smy-drpdwn-list drpdwn-list", type: "button" },
                      "",
                    ),
                  ),
                ),
              ),
            ),
          ),
          div(
            { class: "rish-adjusted-wrap" },
            div(
              { class: "fund-scheme-wrap hide-date" },
              div(
                { class: "ltst-hstcl-wrap" },
                button(
                  { class: "ltst-hstcl-btn active", type: "button" },
                  "Latest",
                ),
                button(
                  { class: "ltst-hstcl-btn", type: "button" },
                  "Historical",
                ),
              ),
              div(
                { class: "fund-scheme-drpdwn cmmn-drpdwn-wrap" },
                span(
                  {
                    class: "fund-scheme-label drpdwn-label",
                    id: "fund-category",
                  },
                  "Fund category:",
                ),
                div(
                  { class: "scheme-drpdown cmmn-select-drpdwn" },
                  button(
                    { class: "scheme-sltxt drpdwn-sltxt", type: "button", "aria-labelledby": "fund-category", "aria-haspopup": "listbox", "aria-expanded": "false" },
                    span({ class: "selected-txt" }, "All"),
                  ),
                  div(
                    { class: "scheme-menu drpdwn-wrap" },
                    div(
                      { class: "drpdwn-menu", role: "listbox", "aria-labelledby": "fund-category" },
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "All",
                      ),
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "Arbitrage Fund",
                      ),
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "Balanced Advantage Fund",
                      ),
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "ELSS",
                      ),
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "Focused Fund",
                      ),
                    ),
                  ),
                ),
              ),
              div(
                { class: "fund-scheme-drpdwn cmmn-drpdwn-wrap" },
                span(
                  {
                    class: "fund-scheme-label drpdwn-label",
                    id: "scheme-category",
                  },
                  "Scheme",
                ),
                div(
                  { class: "scheme-drpdown cmmn-select-drpdwn" },
                  button(
                    { class: "scheme-sltxt drpdwn-sltxt", type: "button", "aria-labelledby": "scheme-category", "aria-haspopup": "listbox", "aria-expanded": "false" },
                    span({ class: "selected-txt" }, "All"),
                  ),
                  div(
                    { class: "scheme-menu drpdwn-wrap" },
                    div(
                      { class: "drpdwn-menu", role: "listbox", "aria-labelledby": "scheme-category" },
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "All",
                      ),
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "Motilal Oswal Focused Fund",
                      ),
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "Motilal Oswal Midcap Fund",
                      ),
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "Motilal Oswal Flexi Cap Fund",
                      ),
                      button(
                        { class: "scheme-list drpdwn-list", type: "button" },
                        "Motilal Oswal ELSS Tax Saver Fund",
                      ),
                    ),
                  ),
                ),
              ),
              div(
                { class: "start-date" },
                p({ class: "start-date-label" }, "Start Date"),
                div(
                  { class: "start-date-wrap", readonly: "readonly" },
                  p({ class: "start-date-value" }, "25/12/2025"),
                  img({
                    class: "calandar-icon",
                    src: "/icons/calendar-ter.svg",
                    alt: "date icon",
                  }),
                ),
              ),
            ),
            div(
              { class: "xlsx-wrap" },
              button(
                { class: "xlsx-btn", type: "button" },
                img({
                  class: "xlsx-icon",
                  src: downloadicon.getAttribute("src"),
                }),
                span({ class: "xlsx-txt" }, downloadtext),
              ),
            ),
          ),
        ),
      ),
    ),
    div(
      { class: "filter-container" },
      div(
        { class: "filter-fields" },
        div(
          { class: "filter-content" },
          div(
            { class: "sticky-fields" },
            div(
              { class: "sort-period-wrapper sticky-wrapper" },
              button(
                { class: "sort-wrapper stcky-btn", type: "button" },
                img({
                  class: "sort-icon stcky-icon",
                  src: "../../icons/sort-icon.svg",
                }),
                span({ class: "sort-txt stcky-txt" }, "Sort"),
              ),
              button(
                { class: "period-wrapper stcky-btn", type: "button" },
                img({
                  class: "period-icon stcky-icon",
                  src: "../../icons/period-icon.svg",
                }),
                span({ class: "period-txt stcky-txt" }, "Select Period"),
              ),
            ),
            div(
              { class: "category-scheme-wrapper sticky-wrapper" },
              button(
                { class: "category-wrapper stcky-btn", type: "button" },
                img({
                  class: "category-icon stcky-icon",
                  src: "../../icons/fundcategory-icon.svg",
                }),
                span({ class: "category-txt stcky-txt" }, "Fund Category"),
              ),
              button(
                { class: "scheme-wrapper stcky-btn", type: "button" },
                img({
                  class: "scheme-icon stcky-icon",
                  src: "../../icons/scheme-icon.svg",
                }),
                span({ class: "scheme-txt stcky-txt" }, "Scheme"),
              ),
            ),
          ),
          div(
            { class: "category-overlay cmmn-overlay" },
            div(
              { class: "category-container cmmn-container" },
              h2(
                { class: "ctgry-text" },
                leftsubtitle.textContent,
                span({ class: "check-count" }, " (0 selected)"),
              ),
              div(
                { class: "ctgrys-filter " },
                ...Array.from(leftside.children).map(
                  (
                    data,
                    index, // Added 'index'
                  ) =>
                    details(
                      { class: "accordion-field" },
                      summary(
                        { class: "accordion-label" },
                        p(
                          { class: "label-txt", id: `ctgry-label-${index}` },
                          data.querySelector("p").textContent,
                        ),
                      ),
                      div(
                        { class: "accordion-body" },
                        div(
                          { class: "slct-clr-btn" },
                          button(
                            { class: "stcl-btn", type: "button" },
                            "Select All",
                          ),
                          button(
                            { class: "stcl-btn", type: "button" },
                            "Clear All",
                          ),
                        ),
                        div(
                          {
                            class: "ctgry-group",
                            // role: "radiogroup",
                            "aria-labelledby": `ctgry-label-${index}`,
                          },
                          ...(index === 0
                            ? [
                              span(
                                {
                                  class: "sr-only",
                                  id: "category-update-hint",
                                },
                                "On selecting the radio button, the main content will be updated.",
                              ),
                            ]
                            : []),
                          ...Array.from(data.querySelector("ul").children).map(
                            (datainner, innerIndex) => {
                              // Added 'innerIndex'
                              const idval = datainner.textContent
                                .split(" ")
                                .join("-")
                                .toLowerCase();

                              const pathLink = window.location.href
                                .split("/")
                                .at(-1);
                              const targetKey = Object.keys(
                                dataMapMoObj.keyvalurl,
                              ).find(
                                (key) =>
                                  dataMapMoObj.keyvalurl[key] ===
                                  datainner.textContent.trim(),
                              );
                              let urlPrefix = "/downloads/";
                              if (window.location.pathname.includes("/aif/")) {
                                urlPrefix = "/aif/downloads/";
                              } else if (
                                window.location.pathname.includes("/pms/")
                              ) {
                                urlPrefix = "/pms/downloads/";
                              } else if (
                                block
                                  .closest(".section")
                                  ?.classList.contains("internationalbusiness")
                              ) {
                                urlPrefix =
                                  "/international-business/downloadib/";
                              }
                              const isChecked = targetKey === pathLink;
                              const computedHref = `${window.location.origin}${urlPrefix}${targetKey || ""}`;
                              return a(
                                {
                                  class: `ctgry-field ${isChecked ? "active-link" : ""}`,
                                  href: computedHref,
                                  "aria-current": isChecked ? "page" : "false",
                                  style: `display: ${idval === "" || datainner.textContent.trim() === "Guidelines for Transmission of Units (AMFI Circular No. 110)" ? "none" : "flex"};`,
                                  onclick: (e) => {
                                    if (window.innerWidth <= 768) {
                                      // 1. Prevent the immediate browser reload/redirect
                                      e.preventDefault();

                                      // 2. Clear out sister link active tracking attributes in the accordion body
                                      const parentGroup =
                                        e.currentTarget.closest(".ctgry-group");
                                      parentGroup
                                        .querySelectorAll(".ctgry-field")
                                        .forEach((sibling) => {
                                          sibling.removeAttribute(
                                            "aria-current",
                                          );
                                          sibling.classList.remove(
                                            "active-link",
                                          );
                                        });

                                      // 3. Stage the locally selected element as visually active
                                      e.currentTarget.setAttribute(
                                        "aria-current",
                                        "page",
                                      );
                                      e.currentTarget.classList.add(
                                        "active-link",
                                      );

                                      // 4. Update global tracking states with clean, trimmed values
                                      const selectedText =
                                        datainner.textContent.trim();
                                      dataMapMoObj.selval = selectedText;
                                      dataMapMoObj.param.category =
                                        dataMapMoObj.keyval[selectedText];

                                      // 5. Fallback safeguard mapping update to guarantee global key tracking matches
                                      if (targetKey) {
                                        dataMapMoObj.keyvalurl[targetKey] =
                                          selectedText;
                                      }
                                    }
                                  },
                                },
                                datainner.textContent,
                              );
                            },
                          ),
                        ),
                      ),
                    ),
                ),
              ),
              div(
                { class: "close-apply-btn" },
                button({ class: "closebtn clap-btn", type: "button" }, "Close"),
                button({ class: "applybtn clap-btn", type: "button" }, "Apply"),
              ),
            ),
          ),
          div(
            { class: "sort-overlay cmmn-overlay" },
            div(
              { class: "sort-container cmmn-container" },
              h3({ class: "sort-text cmmn-text" }, "Sort"),
              div(
                { class: "sort-filter cmmn-filter" },
                p({ class: "arrange-label" }, "Arrange by"),
                div(
                  { class: "sort-filter-body cmmn-filter-body" },
                  div(
                    { class: "sort-field cmmn-field" },
                    input({
                      class: "sort-inp cmmn-inp",
                      type: "radio",
                      id: "latest",
                      name: "sort",
                      checked: "",
                    }),
                    label(
                      { class: "sort-label cmmn-label", for: "latest" },
                      "Latest",
                    ),
                  ),
                  div(
                    { class: "sort-field cmmn-field" },
                    input({
                      class: "sort-inp cmmn-inp",
                      type: "radio",
                      id: "oton",
                      name: "sort",
                    }),
                    label(
                      { class: "sort-label cmmn-label", for: "oton" },
                      "Oldest to Newest",
                    ),
                  ),
                  div(
                    { class: "sort-field cmmn-field" },
                    input({
                      class: "sort-inp cmmn-inp",
                      type: "radio",
                      id: "ntoo",
                      name: "sort",
                    }),
                    label(
                      { class: "sort-label cmmn-label", for: "ntoo" },
                      "Newest to Oldest",
                    ),
                  ),
                ),
              ),
              div(
                { class: "close-apply-btn" },
                button({ class: "closebtn clap-btn", type: "button" }, "Close"),
                button({ class: "applybtn clap-btn", type: "button" }, "Apply"),
              ),
            ),
          ),
          div(
            { class: "period-overlay cmmn-overlay" },
            div(
              { class: "period-container cmmn-container" },
              h3({ class: "period-text cmmn-text" }, "Select Period"),
              div(
                { class: "period-filter cmmn-filter" },
                details(
                  { class: "accordion-field", open: "" },
                  summary(
                    { class: "accordion-label" },
                    p({ class: "label-txt" }, "Month"),
                  ),
                  div(
                    { class: "accordion-body cmmn-filter-body" },
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "jan",
                        name: "month",
                        checked: "",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "jan" },
                        "January",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "fab",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "fab" },
                        "Fabruary",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "march",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "march" },
                        "March",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "april",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "april" },
                        "April",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "may",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "may" },
                        "May",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "june",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "june" },
                        "June",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "july",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "july" },
                        "July",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "aug",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "aug" },
                        "August",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "sept",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "sept" },
                        "September",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "oct",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "oct" },
                        "October",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "nov",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "nov" },
                        "November",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "dec",
                        name: "month",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "dec" },
                        "December",
                      ),
                    ),
                  ),
                ),
                details(
                  { class: "accordion-field", open: "" },
                  summary(
                    { class: "accordion-label" },
                    p({ class: "label-txt" }, "Year"),
                  ),
                  div(
                    { class: "accordion-body cmmn-filter-body" },
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "year1",
                        name: "year",
                        checked: "",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "year1" },
                        "2025",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "year2",
                        name: "year",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "year2" },
                        "2024",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "year3",
                        name: "year",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "year3" },
                        "2023",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "year4",
                        name: "year",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "year4" },
                        "2022",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "year5",
                        name: "year",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "year5" },
                        "2021",
                      ),
                    ),
                    div(
                      { class: "period-field cmmn-field" },
                      input({
                        class: "period-inp cmmn-inp",
                        type: "radio",
                        id: "year6",
                        name: "year",
                      }),
                      label(
                        { class: "period-label cmmn-label", for: "year6" },
                        "2020",
                      ),
                    ),
                  ),
                ),
              ),
              div(
                { class: "close-apply-btn" },
                button({ class: "closebtn clap-btn", type: "button" }, "Close"),
                button({ class: "applybtn clap-btn", type: "button" }, "Apply"),
              ),
            ),
          ),
          div(
            { class: "fund-ctgry-overlay cmmn-overlay" },
            div(
              { class: "fund-ctgry-container cmmn-container" },
              h3({ class: "fund-text cmmn-text" }, "Fund Category"),
              div(
                { class: "fund-filter cmmn-filter" },
                div(
                  { class: "fund-filter-body cmmn-filter-body" },
                  div(
                    { class: "fund-field cmmn-field" },
                    input({
                      class: "fund-inp cmmn-inp",
                      type: "radio",
                      id: "one",
                      name: "fundCtgry",
                      checked: "",
                    }),
                    label(
                      { class: "fund-label cmmn-label", for: "one" },
                      "All",
                    ),
                  ),
                  div(
                    { class: "fund-field cmmn-field" },
                    input({
                      class: "fund-inp cmmn-inp",
                      type: "radio",
                      id: "two",
                      name: "fundCtgry",
                    }),
                    label(
                      { class: "fund-label cmmn-label", for: "two" },
                      "Arbitrage Fund",
                    ),
                  ),
                  div(
                    { class: "fund-field cmmn-field" },
                    input({
                      class: "fund-inp cmmn-inp",
                      type: "radio",
                      id: "three",
                      name: "fundCtgry",
                    }),
                    label(
                      { class: "fund-label cmmn-label", for: "three" },
                      "Balanced Advantage Fund",
                    ),
                  ),
                  div(
                    { class: "fund-field cmmn-field" },
                    input({
                      class: "fund-inp cmmn-inp",
                      type: "radio",
                      id: "four",
                      name: "fundCtgry",
                    }),
                    label(
                      { class: "fund-label cmmn-label", for: "four" },
                      "ELSS",
                    ),
                  ),
                  div(
                    { class: "fund-field cmmn-field" },
                    input({
                      class: "fund-inp cmmn-inp",
                      type: "radio",
                      id: "five",
                      name: "fundCtgry",
                    }),
                    label(
                      { class: "fund-label cmmn-label", for: "five" },
                      "Flexi Cap Fund",
                    ),
                  ),
                  div(
                    { class: "fund-field cmmn-field" },
                    input({
                      class: "fund-inp cmmn-inp",
                      type: "radio",
                      id: "six",
                      name: "fundCtgry",
                    }),
                    label(
                      { class: "fund-label cmmn-label", for: "six" },
                      "Focused Fund",
                    ),
                  ),
                ),
              ),
              div(
                { class: "close-apply-btn" },
                button({ class: "closebtn clap-btn", type: "button" }, "Close"),
                button({ class: "applybtn clap-btn", type: "button" }, "Apply"),
              ),
            ),
          ),
          div(
            { class: "scheme-overlay cmmn-overlay" },
            div(
              { class: "scheme-container cmmn-container" },
              h3({ class: "scheme-text cmmn-text" }, "Scheme"),
              div(
                { class: "scheme-filter cmmn-filter" },
                div(
                  { class: "scheme-filter-body cmmn-filter-body" },
                  div(
                    { class: "scheme-field cmmn-field" },
                    input({
                      class: "scheme-inp cmmn-inp",
                      type: "radio",
                      id: "sone",
                      name: "scheme",
                      checked: "",
                    }),
                    label(
                      { class: "scheme-label cmmn-label", for: "sone" },
                      "All",
                    ),
                  ),
                  div(
                    { class: "scheme-field cmmn-field" },
                    input({
                      class: "scheme-inp cmmn-inp",
                      type: "radio",
                      id: "stwo",
                      name: "scheme",
                    }),
                    label(
                      { class: "scheme-label cmmn-label", for: "stwo" },
                      "Motilal Oswal Focused Fund",
                    ),
                  ),
                  div(
                    { class: "scheme-field cmmn-field" },
                    input({
                      class: "scheme-inp cmmn-inp",
                      type: "radio",
                      id: "sthree",
                      name: "scheme",
                    }),
                    label(
                      { class: "scheme-label cmmn-label", for: "sthree" },
                      "Motilal Oswal Midcap Fund",
                    ),
                  ),
                  div(
                    { class: "scheme-field cmmn-field" },
                    input({
                      class: "scheme-inp cmmn-inp",
                      type: "radio",
                      id: "sfour",
                      name: "scheme",
                    }),
                    label(
                      { class: "scheme-label cmmn-label", for: "sfour" },
                      "Motilal Oswal Flexi Cap Fund",
                    ),
                  ),
                  div(
                    { class: "scheme-field cmmn-field" },
                    input({
                      class: "scheme-inp cmmn-inp",
                      type: "radio",
                      id: "sfive",
                      name: "scheme",
                    }),
                    label(
                      { class: "scheme-label cmmn-label", for: "sfive" },
                      "Motilal Oswal ELSS Tax Saver Fund",
                    ),
                  ),
                  div(
                    { class: "scheme-field cmmn-field" },
                    input({
                      class: "scheme-inp cmmn-inp",
                      type: "radio",
                      id: "ssix",
                      name: "scheme",
                    }),
                    label(
                      { class: "scheme-label cmmn-label", for: "ssix" },
                      "Motilal Oswal Large and Midcap Fund",
                    ),
                  ),
                ),
              ),
              div(
                { class: "close-apply-btn" },
                button({ class: "closebtn clap-btn", type: "button" }, "Close"),
                button({ class: "applybtn clap-btn", type: "button" }, "Apply"),
              ),
            ),
          ),
        ),
      ),
      div(
        { class: "filtered-content" },
        div(
          { class: "pdf-container active" },
          div(
            { class: "full-result-desc" },
            p(
              { class: "result-desc" },
              "Found 207 results for",
              strong({ class: "result-strong" }, "“Nifty”"),
              "there are 53 documents under selected categories.",
            ),
          ),
          div(
            { class: "pdf-list-content" },
            div(
              { class: "pdf-list", style: "display:none" },
              div(
                { class: "pdf-content" },
                h3({ class: "pdf-title" }, "Motilal Oswal BSE Select IPO ETF"),
                div(
                  { class: "pdf-desc" },
                  span({ class: "date-ctgry" }, "13 Nov 2025 "),
                  span({ class: "date-ctgry" }, "Scheme Documents / SID"),
                ),
              ),
              div(
                { class: "pdf-icon" },
                img({ class: "pdf-img", src: "../../icons/pdf-icon.svg" }),
              ),
            ),
            div(
              { class: "pdf-list", style: "display:none" },
              div(
                { class: "pdf-content" },
                h3({ class: "pdf-title" }, "Motilal Oswal BSE Select IPO ETF"),
                div(
                  { class: "pdf-desc" },
                  span({ class: "date-ctgry" }, "13 Nov 2025 "),
                  span({ class: "date-ctgry" }, "Scheme Documents / SID"),
                ),
              ),
              div(
                { class: "pdf-icon" },
                img({ class: "pdf-img", src: "../../icons/pdf-icon.svg" }),
              ),
            ),
            div(
              { class: "pdf-list", style: "display:none" },
              div(
                { class: "pdf-content" },
                h3({ class: "pdf-title" }, "Motilal Oswal BSE Select IPO ETF"),
                div(
                  { class: "pdf-desc" },
                  span({ class: "date-ctgry" }, "13 Nov 2025 "),
                  span({ class: "date-ctgry" }, "Scheme Documents / SID"),
                ),
              ),
              div(
                { class: "pdf-icon" },
                img({ class: "pdf-img", src: "../../icons/pdf-icon.svg" }),
              ),
            ),
          ),
        ),
        div(
          { class: "table-container" },
          div(
            { class: "table-wrapper" },
            table(
              { class: "table-content" },
              thead(
                { class: "tbl-thead" },
                tr(
                  { class: "tbl-thead-tr" },
                  th({ class: "tbl-thead-th" }, "Scheme name"),
                  th({ class: "tbl-thead-th" }, "Benchmark"),
                  th({ class: "tbl-thead-th" }, "Riskometer Scheme"),
                  th({ class: "tbl-thead-th" }, "Riskometer Benchmark"),
                  th({ class: "tbl-thead-th" }, "NAV Date"),
                  th({ class: "tbl-thead-th" }, "NAV Regular"),
                  th({ class: "tbl-thead-th" }, "Return 1 year (%) Regular"),
                  th({ class: "tbl-thead-th" }, "Return 1 year (%) Direct"),
                  th({ class: "tbl-thead-th" }, "Return 1 year (%) Benchmark"),
                ),
              ),
              tbody(
                { class: "tbl-tbody" },
                tr(
                  { class: "tbl-tbody-tr" },
                  td(
                    { class: "tbl-tbody-td" },
                    "Motilal Oswal Large and Midcap Fund",
                  ),
                  td({ class: "tbl-tbody-td" }, "24.02%"),
                  td({ class: "tbl-tbody-td" }, "9.86%"),
                  td({ class: "tbl-tbody-td" }, "32.75%"),
                  td({ class: "tbl-tbody-td" }, "21.43%"),
                  td({ class: "tbl-tbody-td" }, "33.64%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                ),
                tr(
                  { class: "tbl-tbody-tr" },
                  td({ class: "tbl-tbody-td" }, "Motilal Oswal Flexi Cap Fund"),
                  td({ class: "tbl-tbody-td" }, "24.02%"),
                  td({ class: "tbl-tbody-td" }, "9.86%"),
                  td({ class: "tbl-tbody-td" }, "32.75%"),
                  td({ class: "tbl-tbody-td" }, "21.43%"),
                  td({ class: "tbl-tbody-td" }, "33.64%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                ),
                tr(
                  { class: "tbl-tbody-tr" },
                  td(
                    { class: "tbl-tbody-td" },
                    "Motilal Oswal Large and Midcap Fund",
                  ),
                  td({ class: "tbl-tbody-td" }, "24.02%"),
                  td({ class: "tbl-tbody-td" }, "9.86%"),
                  td({ class: "tbl-tbody-td" }, "32.75%"),
                  td({ class: "tbl-tbody-td" }, "21.43%"),
                  td({ class: "tbl-tbody-td" }, "33.64%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                ),
                tr(
                  { class: "tbl-tbody-tr" },
                  td({ class: "tbl-tbody-td" }, "Motilal Oswal Flexi Cap Fund"),
                  td({ class: "tbl-tbody-td" }, "24.02%"),
                  td({ class: "tbl-tbody-td" }, "9.86%"),
                  td({ class: "tbl-tbody-td" }, "32.75%"),
                  td({ class: "tbl-tbody-td" }, "21.43%"),
                  td({ class: "tbl-tbody-td" }, "33.64%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                  td({ class: "tbl-tbody-td" }, "28.31%"),
                ),
              ),
            ),
          ),
          div({ class: "tabel-desc" }, errorscrren),
        ),
        div(
          { class: "no-docs-container" },
          img({
            class: "no-docs-img",
            src: searchnodoc.querySelector("span img").getAttribute("src"),
          }),
          p({ class: "no-docs-desc" }, searchfour.textContent),
        ),
      ),
    ),
  );

  block.append(blockwrapper);
  const accordions = block.querySelectorAll(".ctgrys-filter .accordion-field");
  accordions.forEach((acc) => {
    acc.addEventListener("toggle", () => {
      if (acc.open) {
        accordions.forEach((otherAcc) => {
          if (otherAcc !== acc) {
            otherAcc.removeAttribute("open");
          }
        });
      }
    });
  });
  block
    .querySelector(".ctgrys-filter .accordion-field")
    .setAttribute("open", "");
  let syncCategoryRadioGroups = () => { };
  dataMapMoObj.syncCategoryRadioGroups = () => {
    block
      .querySelectorAll(".ctgry-group")
      .forEach((group) => syncGroupState(group));
  };
  const initCategoryRadioGroups = () => {
    const groups = block.querySelectorAll(".ctgry-group");
    const getVisibleItems = (items) =>
      items.filter((item) => item.style.display !== "none");

    const syncGroupState = (group) => {
      const items = Array.from(group.querySelectorAll(".ctgry-field"));
      const inputs = items.map((item) => item.querySelector(".ctgry-inp"));
      const isCheckboxMode = inputs.some(
        (input) => input && input.type === "checkbox",
      );
      const visibleItems = getVisibleItems(items);

      // group.setAttribute("role", isCheckboxMode ? "group" : "radiogroup");

      items.forEach((item) => {
        const input = item.querySelector(".ctgry-inp");
        if (!input) return;
        const isChecked = !!input.checked;
        const isFocusable = isCheckboxMode
          ? item.style.display !== "none"
          : (visibleItems.find(
            (el) => el.querySelector(".ctgry-inp")?.checked,
          ) || visibleItems[0]) === item;
        item.setAttribute("role", isCheckboxMode ? "checkbox" : "radio");
        item.setAttribute("aria-checked", isChecked ? "true" : "false");
        item.tabIndex = isFocusable ? 0 : -1;
      });
    };

    const selectItem = (group, item, shouldToggle = false) => {
      const input = item.querySelector(".ctgry-inp");
      if (!input || item.style.display === "none") return;
      const isCheckboxMode = input.type === "checkbox";
      if (isCheckboxMode && shouldToggle) {
        input.checked = !input.checked;
      } else {
        if (!isCheckboxMode) {
          group.querySelectorAll(".ctgry-inp").forEach((otherInput) => {
            otherInput.checked = false;
          });
        }
        input.checked = true;
      }
      syncGroupState(group);
      input.dispatchEvent(new Event("change", { bubbles: true }));
    };

    groups.forEach((group) => {
      const items = Array.from(group.querySelectorAll(".ctgry-field"));

      syncGroupState(group);

      items.forEach((item) => {
        // checkbox issue solved after search
        item.addEventListener("click", (event) => {
          const input = item.querySelector(".ctgry-inp");
          if (!input) return;

          if (
            event.target.tagName !== "INPUT" &&
            event.target.tagName !== "LABEL"
          ) {
            const isCheckboxMode = input.type === "checkbox";
            if (isCheckboxMode) {
              input.checked = !input.checked;
            } else {
              input.checked = true;
            }
          }

          if (input.type === "radio") {
            group.querySelectorAll(".ctgry-inp").forEach((otherInput) => {
              if (otherInput !== input) otherInput.checked = false;
            });
          }

          syncGroupState(group);

          if (
            event.target.tagName !== "INPUT" &&
            event.target.tagName !== "LABEL"
          ) {
            input.dispatchEvent(new Event("change", { bubbles: true }));
          }
          item.focus();
        });

        item.addEventListener("keydown", (event) => {
          const { key } = event;
          const input = item.querySelector(".ctgry-inp");
          if (!input) return;
          const isCheckboxMode = input.type === "checkbox";

          if (key === " " || key === "Enter") {
            event.preventDefault();
            selectItem(group, item, isCheckboxMode);
            item.focus();
            return;
          }

          if (isCheckboxMode) return;

          if (
            ["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"].includes(key)
          ) {
            event.preventDefault();
            const visibleItems = getVisibleItems(items);
            if (visibleItems.length === 0) return;
            const currentIndex = visibleItems.indexOf(item);
            const delta = key === "ArrowDown" || key === "ArrowRight" ? 1 : -1;
            const nextIndex =
              (currentIndex + delta + visibleItems.length) %
              visibleItems.length;
            const nextItem = visibleItems[nextIndex];
            selectItem(group, nextItem);
            nextItem.focus();
          }
        });
      });

      group.querySelectorAll(".ctgry-inp").forEach((input) => {
        input.addEventListener("change", () => syncGroupState(group));
      });
    });

    dataMapMoObj.syncCategoryRadioGroups = () => {
      block
        .querySelectorAll(".ctgry-group")
        .forEach((group) => syncGroupState(group));
    };
  };
  initCategoryRadioGroups();

  const dropdownWraps = block.querySelectorAll(".smy-select-drpdwn");

  dropdownWraps.forEach((wrap) => {
    wrap.addEventListener("focusout", (event) => {
      const goingTo = event.relatedTarget;
      if (!goingTo || !wrap.contains(goingTo)) {
        wrap.classList.remove("active");
        wrap.querySelector(".smy-drpdwn-sltxt")?.setAttribute("aria-expanded", "false");
      }
    });
  });

  block.addEventListener("click", (event) => {
    const { target } = event;

    // HANDLE HEADER CLICK (Open/Close)
    const header = target.closest(".smy-drpdwn-sltxt");
    if (header) {
      const parent = header.closest(".smy-select-drpdwn");

      // Close all other dropdowns except the one clicked, and reflect
      // that in aria-expanded so screen readers announce collapsed state.
      dropdownWraps.forEach((el) => {
        if (el !== parent) {
          el.classList.remove("active");
          el.querySelector(".smy-drpdwn-sltxt")?.setAttribute("aria-expanded", "false");
        }
      });

      // Toggle the current one
      const isNowActive = parent.classList.toggle("active");
      header.setAttribute("aria-expanded", isNowActive ? "true" : "false");
      return; // Exit to avoid running list item logic
    }

    // HANDLE LIST ITEM CLICK (Selection)
    const listItem = target.closest(".smy-drpdwn-list");
    if (listItem) {
      const parent = listItem.closest(".smy-select-drpdwn");
      const labeltext = parent.querySelector(".smy-drpdwn-sltxt");
      if (labeltext.textContent.trim() === listItem.textContent.trim()) {
        labeltext.textContent = listItem.textContent.trim();
        parent.classList.remove("active");
        labeltext.setAttribute("aria-expanded", "false");
        return;
      } // If the same item is clicked, do nothing
      // Update text and close
      labeltext.textContent = listItem.textContent.trim();
      if (listItem.closest(".month-year-wrap") !== null) {
        if (listItem.closest(".smy-drpdwn-wrap").querySelector("#sort-label")) {
          dataMapMoObj.param.sort = listItem.textContent.trim();
          // dataMapMoObj.param.year = listItem.textContent.trim();
          dataMapMoObj.syncMobileView(block, dataMapMoObj.param.sort);
          dataMapMoObj.sortrender(block, dataMapMoObj.param); // AP10
        }
        if (
          listItem.closest(".smy-drpdwn-wrap").querySelector("#month-label")
        ) {
          const month = listItem.textContent.trim();
          dataMapMoObj.param.month = month.slice(0, 3).toLowerCase();
          dataMapMoObj.syncMobileView(block, month);
        }
        if (listItem.closest(".smy-drpdwn-wrap").querySelector("#year-label")) {
          dataMapMoObj.param.year = listItem.textContent.trim();
          dataMapMoObj.syncMobileView(block, dataMapMoObj.param.year);
          if (dataMapMoObj.selval === "Scheme Summary Documents") {
            // --- DESKTOP LOGIC: MONTHS ---
            const monthContainer = block
              .querySelector("#month-label")
              .closest(".smy-drpdwn-wrap");
            const monthMenu = monthContainer.querySelector(".drpdwn-menu");
            const monthLabel = monthContainer.querySelector(".drpdwn-sltxt");
            monthLabel.textContent = "";
            dataMapMoObj.param.month = "";
            const selval = dataMapMoObj.keyvaldrop[dataMapMoObj.selval];
            const yeardrop = dataMapMoObj.dropdown[selval];
            let monthsArr = yeardrop[dataMapMoObj.param.year];
            if (monthsArr === undefined) {
              monthsArr = [];
            }
            const monthOrder = [
              "jan",
              "feb",
              "mar",
              "apr",
              "may",
              "jun",
              "jul",
              "aug",
              "sep",
              "oct",
              "nov",
              "dec",
            ];

            monthsArr.sort(
              (a, b) => monthOrder.indexOf(a) - monthOrder.indexOf(b),
            );
            // Filter out undefined/null/invalid months
            monthsArr = monthsArr.filter(
              (m) => m && dataMapMoObj.monthLookup[m],
            );
            const initialMonthShort = monthsArr[0];
            const initialMonthFull =
              dataMapMoObj.monthLookup[initialMonthShort];

            monthMenu.innerHTML = monthsArr
              .map(
                (m) =>
                  `<button class="smy-drpdwn-list drpdwn-list" type="button" data-short="${m}">${dataMapMoObj.monthLookup[m]}</button>`,
              )
              .join("");
            // monthLabel.textContent = initialMonthFull;

            // --- MOBILE LOGIC: MONTHS ---
            const mobileMonthBody = block.querySelector(
              ".period-filter .accordion-field:nth-child(1) .accordion-body",
            );
            if (mobileMonthBody) {
              mobileMonthBody.innerHTML = "";
              mobileMonthBody.innerHTML = monthsArr
                .map(
                  (m) => `
              <div class="period-field cmmn-field">
                <input class="period-inp cmmn-inp" type="radio" id="m-month-${m}" name="mobile-month" ${m === initialMonthShort ? "checked" : ""}>
                <label class="period-label cmmn-label" for="m-month-${m}">${dataMapMoObj.monthLookup[m]}</label>
              </div>
            `,
                )
                .join("");
            }
          }
        }
        if (
          listItem.closest(".smy-drpdwn-wrap").querySelector("#fund-category")
        ) {
          dataMapMoObj.param.fundcategory = listItem.textContent.trim();
          dataMapMoObj.syncMobileView(block, dataMapMoObj.param.fundcategory);
        }
        if (
          listItem.closest(".smy-drpdwn-wrap").querySelector("#scheme-category")
        ) {
          dataMapMoObj.param.schemecategory = listItem.textContent.trim();
          dataMapMoObj.syncMobileView(block, dataMapMoObj.param.schemecategory);
        }
        if (
          window.innerWidth > 768 &&
          !listItem.closest(".smy-drpdwn-wrap").querySelector("#sort-label")
        ) {
          const arr = [
            "KYC & Redressal of Complaints",
            "Guidelines for Transmission of Units (AMFI Circular No. 110)",
            "Remunerations",
            "AMFI IAP",
            "Grievance Redressal Mechanism",
            "Disclosure of Empanelment Details of Mutual Fund Distributors",
            "Disclosure of Empanelment Details of PMS Distributors"
          ];
          if (dataMapMoObj.selval === "Scheme Summary Documents") {
            if (block.querySelector(".download-pagination-footer")) {
              block.querySelector(".download-pagination-footer").remove();
            }
            const pdfContainer = block.querySelector(
              ".pdf-container .pdf-list-content",
            );
            const results = dataMapMoObj?.results?.filter((element) => {
              const yearMatch = dataMapMoObj.param.year
                ? element.year === dataMapMoObj.param.year
                : true;
              const monthMatch = dataMapMoObj.param.month
                ? element.month === dataMapMoObj.param.month
                : true;

              return yearMatch && monthMatch;
            });
            // console.log(results);
            const sortResults = (data, direction = "newest") =>
              [...data].sort((a, b) => {
                // Standardizing "DD-MM-YYYY" to "YYYY-MM-DD" for Date parsing
                const dateA = new Date(
                  a.publishDate.split("-").reverse().join("-"),
                );
                const dateB = new Date(
                  b.publishDate.split("-").reverse().join("-"),
                );

                if (direction === "newest") {
                  return dateB - dateA; // High to Low (Dec 2024 -> Jan 2024)
                }
                return dateA - dateB; // Low to High (Jan 2024 -> Dec 2024)
              });

            let resultArr = [];

            // Apply the sorting based on the parameter
            if (
              dataMapMoObj.param.sort === "Latest" ||
              dataMapMoObj.param.sort === "Newest to Oldest"
            ) {
              resultArr = sortResults(results, "newest");
            } else if (dataMapMoObj.param.sort === "Oldest to Newest") {
              resultArr = sortResults(results, "oldest");
            } else {
              // Default fallback
              resultArr = results;
            }
            // Render grouped cards for Scheme Summary Documents
            const pdfListHTML =
              dataMapMoObj.renderSchemeSummaryCards(resultArr);

            // 4. Update the DOM exactly once
            pdfContainer.innerHTML = "";
            pdfContainer.innerHTML = pdfListHTML;
            block.querySelector(".pdf-container").classList.add("active");
            const items = Array.from(
              block.querySelectorAll(".pdf-container .pdf-list"),
            );
            const itemsPerPage = items.slice(0, 9).length;
            if (items.length > itemsPerPage) {
              dataMapMoObj.setupPagination(block, items, itemsPerPage);
            }
            dataMapMoObj.handleDownload = (url, fileName) => {
              fetch(url)
                .then((response) => {
                  if (!response.ok) throw new Error("Network error");
                  return response.blob();
                })
                .then((blob) => {
                  const blobUrl = window.URL.createObjectURL(blob);
                  const alink = document.createElement("a");

                  // Critical: Set these attributes for iOS compatibility
                  alink.style.display = "none";
                  alink.href = blobUrl;
                  alink.download = fileName;
                  alink.target = "_blank"; // Helpful for mobile Safari fallback

                  document.body.appendChild(alink); // FIXED: was 'a', now 'alink'
                  alink.click();

                  // Cleanup
                  setTimeout(() => {
                    window.URL.revokeObjectURL(blobUrl);
                    alink.remove();
                  }, 100);
                })
                .catch((err) => {
                  console.error("Download failed, falling back:", err);
                  // Fallback: Open in new tab if Fetch/CORS fails
                  window.open(url, "_blank");
                });
            };
          } else if (
            dataMapMoObj.dropEvent === "" &&
            dataMapMoObj.selval !==
            "Risk Adjusted Returns - Information Ratio (IR)"
          ) {
            dataMapMoObj.categoryfilter(block, dataMapMoObj.param);
          } else if (arr.includes(dataMapMoObj.selval)) {
            if (block.querySelector(".download-pagination-footer")) {
              block.querySelector(".download-pagination-footer").remove();
            }
            block.querySelector(".pdf-container").classList.remove("active");
            block
              .querySelector(".download-container")
              .classList.add("tab-text-active");
            return false;
          }
        }
        block.querySelector(".ctgry-filter-inp").value = "";
        block.querySelector(".ctgry-filter-inp").value = dataMapMoObj.selval;
        block.querySelector(".ctgry-filter-drpdwn").classList.add("active");
      }
      parent.classList.remove("active");
      labeltext.setAttribute("aria-expanded", "false");
    }
  });

  // OPTIONAL: Close dropdowns if clicking anywhere else on the page
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".smy-drpdwn-wrap")) {
      dropdownWraps.forEach((el) => {
        el.classList.remove("active");
        el.querySelector(".smy-drpdwn-sltxt")?.setAttribute("aria-expanded", "false");
      });
    }
    if (!e.target.closest(".cmmn-select-drpdwn")) {
      Array.from(block.querySelectorAll(".cmmn-select-drpdwn")).forEach(
        (dropdwnin) => {
          dropdwnin.classList.remove("active");
        },
      );
    }
  });

  block.querySelector(".ctgry-filter-inp").addEventListener("click", () => {
    block
      .querySelector(".filter-container .category-overlay")
      .classList.add("active");
    block.closest("body").classList.add("scroll-stop");
  });

  Array.from(block.querySelectorAll(".close-apply-btn .closebtn ")).forEach(
    (elementfor) => {
      elementfor.addEventListener("click", () => {
        elementfor.closest(".cmmn-overlay").classList.remove("active");
        block.closest("body").classList.remove("scroll-stop");
      });
    },
  );

  Array.from(block.querySelectorAll(".close-apply-btn .applybtn")).forEach(
    (elementfor) => {
      elementfor.addEventListener("click", (event) => {
        event.preventDefault;
        elementfor.closest(".cmmn-overlay").classList.remove("active");
        block.closest("body").classList.remove("scroll-stop");
        // dataMapMoObj.sub = event.target.closest('.accordion-field')
        //   .querySelector('.accordion-label').textContent.trim();
        if (dataMapMoObj.selval !== undefined) {
          block.querySelector(".ctgry-filter-inp").value = dataMapMoObj.selval;
          block.querySelector(".ctgry-filter-drpdwn").classList.add("active");
          if (elementfor.closest(".period-overlay")) {
            const categorybk = dataMapMoObj.getSelectedFilters(block);
            const tempmonth = categorybk?.month
              ?.slice(0, 3)
              .toLocaleLowerCase();
            const tempyear = categorybk?.year;
            const category = categorybk?.category;
            if (
              dataMapMoObj.param.year !== tempyear ||
              dataMapMoObj.dropdown[dataMapMoObj.keyvaldrop[category]][
                tempyear
              ].indexOf(tempmonth) === -1
            ) {
              dataMapMoObj.param.month = "";
              // dataMapMoObj.dropdown[dataMapMoObj.keyvaldrop[category]][tempyear][0];
              const yearContainer = block
                .querySelector("#year-label")
                .closest(".smy-drpdwn-wrap");
              const yearMenu = yearContainer.querySelector(".drpdwn-menu");
              const yearLabel = yearContainer.querySelector(".drpdwn-sltxt");
              // Render Desktop Years
              yearMenu.innerHTML = dataMapMoObj.sortedKeys
                .map(
                  (yr) =>
                    `<button class="smy-drpdwn-list drpdwn-list" type="button">${yr}</button>`,
                )
                .join("");
              // yearLabel.textContent = initialYear;

              // --- MOBILE LOGIC: YEARS ---
              const mobileYearBody = block.querySelector(
                ".period-filter .accordion-field:nth-child(2) .accordion-body",
              );
              if (mobileYearBody) {
                mobileYearBody.innerHTML = dataMapMoObj.sortedKeys
                  .map(
                    (yr, index) => `
              <div class="period-field cmmn-field">
                <input class="period-inp cmmn-inp" type="radio" id="m-year-${yr}" name="mobile-year" ${yr === tempyear ? "checked" : ""}>
                <label class="period-label cmmn-label" for="m-year-${yr}">${yr}</label>
              </div>
            `,
                  )
                  .join("");
              }

              // --- DESKTOP LOGIC: MONTHS ---
              const monthContainer = block
                .querySelector("#month-label")
                .closest(".smy-drpdwn-wrap");
              const monthMenu = monthContainer.querySelector(".drpdwn-menu");
              const monthLabel = monthContainer.querySelector(".drpdwn-sltxt");
              let monthsArr =
                dataMapMoObj.dropdown[dataMapMoObj.keyvaldrop[category]][
                tempyear
                ];
              if (monthsArr === undefined) {
                monthsArr = [];
              }
              const monthOrder = [
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
              ];

              monthsArr.sort(
                (a, b) => monthOrder.indexOf(a) - monthOrder.indexOf(b),
              );
              // Filter out undefined/null/invalid months
              monthsArr = monthsArr.filter(
                (m) => m && dataMapMoObj.monthLookup[m],
              );
              const initialMonthShort = monthsArr[0];
              const initialMonthFull =
                dataMapMoObj.monthLookup[initialMonthShort];

              monthMenu.innerHTML = monthsArr
                .map(
                  (m) =>
                    `<button class="smy-drpdwn-list drpdwn-list" type="button" data-short="${m}">${dataMapMoObj.monthLookup[m]}</button>`,
                )
                .join("");
              // monthLabel.textContent = initialMonthFull;

              // --- MOBILE LOGIC: MONTHS ---
              const mobileMonthBody = block.querySelector(
                ".period-filter .accordion-field:nth-child(1) .accordion-body",
              );
              if (mobileMonthBody) {
                mobileMonthBody.innerHTML = monthsArr
                  .map(
                    (m) => `
              <div class="period-field cmmn-field">
                <input class="period-inp cmmn-inp" type="radio" id="m-month-${m}" name="mobile-month" ${m === initialMonthShort ? "checked" : ""}>
                <label class="period-label cmmn-label" for="m-month-${m}">${dataMapMoObj.monthLookup[m]}</label>
              </div>
            `,
                  )
                  .join("");
              }
              dataMapMoObj.param.month = initialMonthShort;
              dataMapMoObj.syncMobileView(block, initialMonthFull);
            } else {
              dataMapMoObj.param.month = categorybk.month
                .slice(0, 3)
                .toLowerCase();
            }
            // dataMapMoObj.param.month = categorybk.month.slice(0, 3).toLowerCase();
            dataMapMoObj.param.year = categorybk.year;
            const arr = [
              "KYC & Redressal of Complaints",
              "Guidelines for Transmission of Units (AMFI Circular No. 110)",
              "Remunerations",
              "AMFI IAP",
              "Grievance Redressal Mechanism",
              "Disclosure of Empanelment Details of Mutual Fund Distributors",
              "Disclosure of Empanelment Details of PMS Distributors"
            ];
            // AJ27
            if (dataMapMoObj.selval === "Scheme Summary Documents") {
              // --- DESKTOP LOGIC: MONTHS ---
              const monthContainer = block
                .querySelector("#month-label")
                .closest(".smy-drpdwn-wrap");
              const monthMenu = monthContainer.querySelector(".drpdwn-menu");
              const monthLabel = monthContainer.querySelector(".drpdwn-sltxt");
              monthLabel.textContent = "";
              if (dataMapMoObj.param.year !== tempyear) {
                dataMapMoObj.param.month = "";
              }
              const selval = dataMapMoObj.keyvaldrop[dataMapMoObj.selval];
              const yeardrop = dataMapMoObj.dropdown[selval];
              let monthsArr = yeardrop[dataMapMoObj.param.year];
              if (monthsArr === undefined) {
                monthsArr = [];
              }
              const monthOrder = [
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
              ];

              monthsArr.sort(
                (a, b) => monthOrder.indexOf(a) - monthOrder.indexOf(b),
              );
              const initialMonthShort = dataMapMoObj.param.month;
              const initialMonthFull =
                dataMapMoObj.monthLookup[initialMonthShort];

              monthMenu.innerHTML = monthsArr
                .map(
                  (m) =>
                    `<button class="smy-drpdwn-list drpdwn-list" type="button" data-short="${m}">${dataMapMoObj.monthLookup[m]}</button>`,
                )
                .join("");
              // monthLabel.textContent = initialMonthFull;

              // --- MOBILE LOGIC: MONTHS ---
              const mobileMonthBody = block.querySelector(
                ".period-filter .accordion-field:nth-child(1) .accordion-body",
              );
              if (mobileMonthBody) {
                mobileMonthBody.innerHTML = "";
                mobileMonthBody.innerHTML = monthsArr
                  .map(
                    (m) => `
              <div class="period-field cmmn-field">
                <input class="period-inp cmmn-inp" type="radio" id="m-month-${m}" name="mobile-month" ${m === initialMonthShort ? "checked" : ""}>
                <label class="period-label cmmn-label" for="m-month-${m}">${dataMapMoObj.monthLookup[m]}</label>
              </div>
            `,
                  )
                  .join("");
              }
              if (block.querySelector(".download-pagination-footer")) {
                block.querySelector(".download-pagination-footer").remove();
              }
              const pdfContainer = block.querySelector(
                ".pdf-container .pdf-list-content",
              );
              const results = dataMapMoObj?.results?.filter((element) => {
                const yearMatch = dataMapMoObj.param.year
                  ? element.year === dataMapMoObj.param.year
                  : true;
                const monthMatch = dataMapMoObj.param.month
                  ? element.month === dataMapMoObj.param.month
                  : true;

                return yearMatch && monthMatch;
              });
              // console.log(results);
              const sortResults = (data, direction = "newest") =>
                [...data].sort((a, b) => {
                  // Standardizing "DD-MM-YYYY" to "YYYY-MM-DD" for Date parsing
                  const dateA = new Date(
                    a.publishDate.split("-").reverse().join("-"),
                  );
                  const dateB = new Date(
                    b.publishDate.split("-").reverse().join("-"),
                  );

                  if (direction === "newest") {
                    return dateB - dateA; // High to Low (Dec 2024 -> Jan 2024)
                  }
                  return dateA - dateB; // Low to High (Jan 2024 -> Dec 2024)
                });

              let resultArr = [];

              // Apply the sorting based on the parameter
              if (
                dataMapMoObj.param.sort === "Latest" ||
                dataMapMoObj.param.sort === "Newest to Oldest"
              ) {
                resultArr = sortResults(results, "newest");
              } else if (dataMapMoObj.param.sort === "Oldest to Newest") {
                resultArr = sortResults(results, "oldest");
              } else {
                // Default fallback
                resultArr = results;
              }
              // Render grouped cards for Scheme Summary Documents
              const pdfListHTML =
                dataMapMoObj.renderSchemeSummaryCards(resultArr);

              // 4. Update the DOM exactly once
              pdfContainer.innerHTML = "";
              pdfContainer.innerHTML = pdfListHTML;
              block.querySelector(".pdf-container").classList.add("active");
              const items = Array.from(
                block.querySelectorAll(".pdf-container .pdf-list"),
              );
              const itemsPerPage = items.slice(0, 9).length;
              if (items.length > itemsPerPage) {
                dataMapMoObj.setupPagination(block, items, itemsPerPage);
              }
              dataMapMoObj.handleDownload = (url, fileName) => {
                fetch(url)
                  .then((response) => {
                    if (!response.ok) throw new Error("Network error");
                    return response.blob();
                  })
                  .then((blob) => {
                    const blobUrl = window.URL.createObjectURL(blob);
                    const alink = document.createElement("a");

                    // Critical: Set these attributes for iOS compatibility
                    alink.style.display = "none";
                    alink.href = blobUrl;
                    alink.download = fileName;
                    alink.target = "_blank"; // Helpful for mobile Safari fallback

                    document.body.appendChild(alink); // FIXED: was 'a', now 'alink'
                    alink.click();

                    // Cleanup
                    setTimeout(() => {
                      window.URL.revokeObjectURL(blobUrl);
                      alink.remove();
                    }, 100);
                  })
                  .catch((err) => {
                    console.error("Download failed, falling back:", err);
                    // Fallback: Open in new tab if Fetch/CORS fails
                    window.open(url, "_blank");
                  });
              };
              return false;
            }
            if (
              dataMapMoObj.dropEvent === "" &&
              dataMapMoObj.selval !==
              "Risk Adjusted Returns - Information Ratio (IR)"
            ) {
              dataMapMoObj.categoryfilter(block, dataMapMoObj.param);
            } else if (arr.includes(dataMapMoObj.selval)) {
              block.querySelector(".pdf-container").classList.remove("active");
              block
                .querySelector(".download-container")
                .classList.add("tab-text-active");
              return false;
            }
            block
              .querySelector("#month-label")
              .closest(".smy-drpdwn-wrap")
              .querySelector(".drpdwn-sltxt").textContent = "";
            block
              .querySelector("#year-label")
              .closest(".smy-drpdwn-wrap")
              .querySelector(".drpdwn-sltxt").textContent = "";
            block
              .querySelector("#month-label")
              .closest(".smy-drpdwn-wrap")
              .querySelector(".drpdwn-sltxt").textContent = categorybk.month;
            block
              .querySelector("#year-label")
              .closest(".smy-drpdwn-wrap")
              .querySelector(".drpdwn-sltxt").textContent = categorybk.year;
          }
          if (elementfor.closest(".sort-overlay")) {
            const categorybk = dataMapMoObj.getSelectedFilters(block);
            dataMapMoObj.param.sort = categorybk.sort;
            dataMapMoObj.sortrender(block, dataMapMoObj.param);
            block
              .querySelector("#sort-label")
              .closest(".smy-drpdwn-wrap")
              .querySelector(".drpdwn-sltxt").textContent = "";
            block
              .querySelector("#sort-label")
              .closest(".smy-drpdwn-wrap")
              .querySelector(".drpdwn-sltxt").textContent = categorybk.sort;
          }
          if (elementfor.closest(".category-overlay")) {
            const categorybk = dataMapMoObj.getSelectedFilters(block);
            dataMapMoObj.selval = categorybk.category;
            dataMapMoObj.param.category =
              dataMapMoObj.keyval[categorybk.category];
            block.querySelector(".ctgry-filter-inp").value = "";
            block.querySelector(".ctgry-filter-inp").value =
              dataMapMoObj.selval;
            block.querySelector(".ctgry-filter-drpdwn").classList.add("active");
            const checkboxp = elementfor
              .closest(".category-overlay")
              .querySelectorAll('[type="checkbox"]');
            if (checkboxp.length === 0) {
              const targetValue = dataMapMoObj.selval;
              const targetKey = Object.keys(dataMapMoObj.keyvalurl).find(
                (key) => dataMapMoObj.keyvalurl[key] === targetValue,
              );
              // console.log(targetKey)
              const classList = Array.from(block.closest(".section").classList);
              const link = window.location.origin;
              // if (window.location.origin.includes('motilaloswalamc')) {
              //   link = window.location.origin.replace('amc', 'mf');
              // }
              if (classList.includes("internationalbusiness")) {
                window.location.href = `${link}/international-business/downloadib/${targetKey}`;
              } else if (window.location.pathname.includes("/aif/")) {
                window.location.href = `${link}/aif/downloads/${targetKey}`;
              } else if (window.location.pathname.includes("/pms/")) {
                window.location.href = `${link}/pms/downloads/${targetKey}`;
              } else {
                window.location.href = `${link}/downloads/${targetKey}`;
              }
              return false;
            }
            Array.from(
              block.querySelectorAll(".filtered-content .section"),
            ).forEach((tabTextSection) => {
              if (dataMapMoObj.dropEvent === "") {
                if (
                  tabTextSection.getAttribute("data-id") ===
                  dataMapMoObj.selval.toLowerCase().split(" ").join("-")
                ) {
                  Array.from(
                    block.querySelectorAll(".filtered-content div"),
                  ).forEach((ele) => {
                    ele.classList.remove("active");
                  });
                  tabTextSection.classList.add("active");
                }
              }
            });
            const arr = [
              "KYC & Redressal of Complaints",
              "Guidelines for Transmission of Units (AMFI Circular No. 110)",
              "Remunerations",
              "AMFI IAP",
              "Grievance Redressal Mechanism",
              "Disclosure of Empanelment Details of Mutual Fund Distributors",
              "Disclosure of Empanelment Details of PMS Distributors"
            ];
            const riskupper = block.querySelector(".upper-filter");
            riskupper.classList.remove("risk-return-active");
            block
              .querySelector(".filter-content .sticky-fields")
              .classList.remove("risk-return-active");
            if (arr.includes(dataMapMoObj.selval)) {
              if (block.querySelector(".download-pagination-footer")) {
                block.querySelector(".download-pagination-footer").remove();
              }
              block
                .querySelector(".download-container")
                .classList.add("tab-text-active");
              return false;
            }
            block
              .querySelector(".download-container")
              .classList.remove("tab-text-active");
            const arrval = [
              "KYC & Redressal of Complaints",
              "Guidelines for Transmission of Units (AMFI Circular No. 110)",
              "Remunerations",
              "Grievance Redressal Mechanism",
              "Disclosure of Empanelment Details of Mutual Fund Distributors",
              "Disclosure of Empanelment Details of PMS Distributors"
            ];
            if (
              dataMapMoObj.selval ===
              "Risk Adjusted Returns - Information Ratio (IR)"
            ) {
              dataMapMoObj.riskAdjustment(block);
            } else if (arrval.includes(dataMapMoObj.selval)) {
              block.querySelector(".pdf-container").classList.remove("active");
              block
                .querySelector(".download-container")
                .classList.add("tab-text-active");
              return false;
            } else {
              const checkboxp = elementfor
                .closest(".category-overlay")
                .querySelectorAll('[type="checkbox"]');
              if (checkboxp.length === 0) {
                dataMapMoObj.categoryfilter(block, dataMapMoObj.param);
              }
            }
          }
          if (dataMapMoObj.dropEvent === "") {
            // dataMapMoObj.renderdrop(block);
          }
        }
      });
    },
  );

  block.querySelector(".sort-wrapper").addEventListener("click", () => {
    block.querySelector(".sort-overlay").classList.add("active");
    block.closest("body").classList.add("scroll-stop");
  });

  block.querySelector(".period-wrapper").addEventListener("click", () => {
    block.querySelector(".period-overlay").classList.add("active");
    block.closest("body").classList.add("scroll-stop");
  });

  block.querySelector(".category-wrapper").addEventListener("click", () => {
    block.querySelector(".fund-ctgry-overlay").classList.add("active");
    block.closest("body").classList.add("scroll-stop");
  });

  block.querySelector(".scheme-wrapper").addEventListener("click", () => {
    block.querySelector(".scheme-overlay").classList.add("active");
    block.closest("body").classList.add("scroll-stop");
  });


  Array.from(
    block.querySelectorAll(".fund-scheme-wrap .cmmn-drpdwn-wrap .drpdwn-sltxt"),
  ).forEach((dropdwn) => {
    dropdwn.addEventListener("click", () => {
      Array.from(block.querySelectorAll(".cmmn-select-drpdwn")).forEach(
        (dropdwnin) => {
          dropdwnin.classList.remove("active");
        },
      );
      dropdwn.closest(".cmmn-select-drpdwn").classList.add("active");
    });
  });

  Array.from(
    block.querySelectorAll(".fund-scheme-drpdwn .drpdwn-list"),
  ).forEach((elementlist) => {
    elementlist.addEventListener("click", () => {
      const elm = elementlist
        .closest(".scheme-drpdown")
        .querySelector(".drpdwn-sltxt");
      elm.textContent = "";
      elm.textContent = elementlist.textContent.trim();
      elementlist.closest(".scheme-drpdown").classList.remove("active");
    });
  });
  const filterContainer = block.querySelector(".ctgrys-filter");

  function handleSelection(radioElement) {
    const selectedText = radioElement;
    // .nextElementSibling.textContent.trim();
    const dataIdMatch = selectedText.toLowerCase().replace(/\s+/g, "-");
    dataMapMoObj.selval = selectedText;
    dataMapMoObj.param.category = dataMapMoObj.keyval[selectedText];
    // 1. Specialized Logic: Risk Adjusted Returns
    if (selectedText === "Risk Adjusted Returns - Information Ratio (IR)") {
      dataMapMoObj.riskAdjustment(block);
    } else {
      block
        .querySelector(".upper-filter")
        ?.classList.remove("risk-return-active");
      block
        .querySelector(".filter-content .sticky-fields")
        ?.classList.remove("risk-return-active");
      activateSection(".pdf-container");
    }

    // 2. Section Toggling by Data-ID
    const sections = block.querySelectorAll(".filtered-content .section");
    sections.forEach((sec) => {
      if (sec.getAttribute("data-id") === dataIdMatch) {
        sec.parentElement
          .querySelectorAll("div")
          .forEach((el) => el.classList.remove("active"));
        sec.classList.add("active");
      }
    });

    // 3. Specialized Logic: Compliance Tabs
    const complianceTabs = [
      "KYC & Redressal of Complaints",
      "Guidelines for Transmission of Units (AMFI Circular No. 110)",
      "Remunerations",
      "AMFI IAP",
      "Grievance Redressal Mechanism",
      "Disclosure of Empanelment Details of Mutual Fund Distributors",
      "Disclosure of Empanelment Details of PMS Distributors"
    ];
    const downloadContainer = block.querySelector(".download-container");

    if (complianceTabs.includes(selectedText)) {
      if (block.querySelector(".download-pagination-footer")) {
        block.querySelector(".download-pagination-footer").remove();
      }
      downloadContainer.classList.add("tab-text-active");
      return false; // Exit: No API, No Mobile UI Header Update
    }
    if (dataMapMoObj.dropdown !== undefined) {
      dataMapMoObj.renderdrop(block);
    }
    downloadContainer.classList.remove("tab-text-active");

    // 4. API Sync & Mobile UI Header Update
    syncFilterParams(selectedText);
    if (window.innerWidth < 786) {
      updateMobileUI(selectedText);
    }
  }

  // Helpers
  function activateSection(selector) {
    const container = block.querySelector(".filtered-content");
    if (container) {
      Array.from(container.children).forEach((el) =>
        el.classList.remove("active"),
      );
      container.querySelector(selector)?.classList.add("active");
    }
  }

  function syncFilterParams(selectedText) {
    dataMapMoObj.param.category = dataMapMoObj.keyval[selectedText];
    const getVal = (id) =>
      block
        .querySelector(id)
        ?.closest(".smy-drpdwn-wrap")
        .querySelector(".drpdwn-sltxt")
        .textContent.trim();
    dataMapMoObj.getVal = getVal;
    dataMapMoObj.param.year = getVal("#year-label");
    dataMapMoObj.param.month = getVal("#month-label").slice(0, 3).toLowerCase();

    if (
      dataMapMoObj.dropEvent === "" &&
      dataMapMoObj.selval !==
      "Risk Adjusted Returns - Information Ratio (IR)" &&
      dataMapMoObj.param.year !== "" &&
      dataMapMoObj.param.month !== ""
    ) {
      dataMapMoObj.categoryfilter(block, dataMapMoObj.param);
    } else if (dataMapMoObj.selval === "Scheme Summary Documents") {
      dataMapMoObj.categoryfilter(block, dataMapMoObj.param);
    }
  }

  function updateMobileUI(text) {
    const complianceTabs = [
      "KYC & Redressal of Complaints",
      "Guidelines for Transmission of Units (AMFI Circular No. 110)",
      "Remunerations",
      "Grievance Redressal Mechanism",
      "Disclosure of Empanelment Details of Mutual Fund Distributors",
      "Disclosure of Empanelment Details of PMS Distributors"
    ];
    if (
      text === "Risk Adjusted Returns - Information Ratio (IR)" ||
      complianceTabs.includes(text)
    )
      return;

    const input = block.querySelector(".ctgry-filter-inp");
    if (input) input.value = text;
    block.querySelector(".ctgry-filter-drpdwn")?.classList.add("active");
  }

  dataMapMoObj.param.sort = block
    .querySelector("#sort-label")
    .closest(".smy-drpdwn-wrap")
    .querySelector(".drpdwn-sltxt")
    .textContent.trim();

  // 1. Check on Page Load
  const pathLink = window.location.href.split("/").at(-1);
  const initialChecked = dataMapMoObj.keyvalurl[pathLink];
  const selecaterogy = (param, options = {}) => {
    const { shouldScroll = true } = options;
    const selectedValueFromMap = param;

    if (selectedValueFromMap) {
      // 1. Find all labels in the filter
      const allLabels = document.querySelectorAll(
        ".ctgrys-filter .ctgry-field",
      );

      // 2. Loop through labels to find the one matching our text
      const targetLabel = Array.from(allLabels).find(
        (label) => label.textContent.trim() === selectedValueFromMap,
      );

      if (targetLabel) {
        // 3. Find the radio button (it is the previous sibling of the label)

        // 4. Handle Accordion: Open the parent, close all others
        const targetAccordion = targetLabel.closest(".accordion-field");

        block
          .querySelectorAll(".category-overlay .accordion-field")
          .forEach((acc) => {
            // If this is the parent of our matched label, open it. Otherwise, close it.
            if (acc === targetAccordion) {
              acc.setAttribute("open", "");
            } else {
              acc.removeAttribute("open");
            }
          });

        // 5. Scroll to the active accordion for better UX
        if (shouldScroll) {
          targetAccordion.scrollIntoView({
            behavior: "smooth",
            block: "nearest",
          });
        }
      }
    }
    // if (window.innerWidth < 768) {
    block.querySelector(".ctgry-filter-inp").value = "";
    block.querySelector(".ctgry-filter-inp").value = initialChecked;
    block.querySelector(".ctgry-filter-drpdwn").classList.add("active");
    if (dataMapMoObj.dropEvent === "Y") {
      return false;
    }
    return param;
  };
  dataMapMoObj.selecaterogy = selecaterogy;
  dataMapMoObj.selecaterogy(initialChecked);
  // Show Particular Tab Text Content
  const mainWrap = block.closest("main");
  const filterWrap = mainWrap.querySelector(
    ".download-container .filter-container",
  );
  const rightContainer = filterWrap.querySelector(".filtered-content");
  const alldataId = [
    "remunerations",
    "kyc-&-redressal-of-complaints",
    "guidelines-for-transmission-of-units-(amfi-circular-no.-110)",
    "amfi-iap",
    "grievance-redressal-mechanism",
    "disclosure-of-empanelment-details-of-mutual-fund-distributors",
    "disclosure-of-empanelment-details-of-pms-distributors"
  ];
  mainWrap.querySelectorAll(".section").forEach((ele) => {
    if (alldataId.includes(ele.getAttribute("data-id"))) {
      ele.classList.add("download-tab-content");
      rightContainer.append(ele);
      dataMapMoObj.CLASS_PREFIXES = [
        "remunation",
        "mainremunation",
        "maininnerremu",
        "subremunation",
        "subinnuremu",
        "containremu",
        "containnerremu",
      ];
      dataMapMoObj.addIndexed(ele);
    }
  });
  // Open disclosure-of-empanelment button in a new tab
  let empanelmentSection = rightContainer.querySelector('.section[data-id="disclosure-of-empanelment-details-of-mutual-fund-distributors"]');
  if (!empanelmentSection) {
    empanelmentSection = rightContainer.querySelector('.section[data-id="disclosure-of-empanelment-details-of-pms-distributors"]');
  }
  if (empanelmentSection) {
    empanelmentSection.querySelectorAll('.button-container a').forEach((a) => {
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
    });
  }

  // block.querySelector('.ctgry-inp:checked');
  if (initialChecked) handleSelection(initialChecked);
  // 2. Check on Change
  filterContainer.addEventListener("change", (event) => {
    if (
      event.target.classList.contains("ctgry-inp") &&
      window.innerWidth > 768 &&
      event.target.getAttribute("type") !== "checkbox"
    ) {
      const targetValue = event.target.nextElementSibling.textContent.trim();
      const targetKey = Object.keys(dataMapMoObj.keyvalurl).find(
        (key) => dataMapMoObj.keyvalurl[key] === targetValue,
      );
      // console.log(targetKey)
      const classList = Array.from(block.closest(".section").classList);
      const link = window.location.origin;
      // if (window.location.origin.includes('motilaloswalamc')) {
      //   link = window.location.origin.replace('amc', 'mf');
      // }
      if (classList.includes("internationalbusiness")) {
        window.location.href = `${link}/international-business/downloadib/${targetKey}`;
      } else if (window.location.pathname.includes("/aif/")) {
        window.location.href = `${link}/aif/downloads/${targetKey}`;
      } else if (window.location.pathname.includes("/pms/")) {
        window.location.href = `${link}/pms/downloads/${targetKey}`;
      } else {
        window.location.href = `${link}/downloads/${targetKey}`;
      }
      // handleSelection(event.target);
    }
    dataMapMoObj.sub = event.target
      .closest(".accordion-field")
      .querySelector(".accordion-label")
      .textContent.trim();
  });

  const initDatePicker = (wrapperEl) => {
    if (!wrapperEl) return;

    // 1. Find the specific element that displays the date
    const dateValueEl = wrapperEl.querySelector(".start-date-value");

    const fp = flatpickr(wrapperEl, {
      dateFormat: "d/m/Y",
      disableMobile: true,
      clickOpens: false,
      onChange: (selectedDates, dateStr) => {
        // 2. Update the .start-date-value text when a date is picked
        if (dateValueEl) {
          dateValueEl.textContent = dateStr;
          dataMapMoObj.dateVal = dateValueEl.textContent;
          // onchange
          dataMapMoObj.selectTab = "HistoricalDate";
          dataMapMoObj.riskAdjustment(block);
        }
      },
      // Optional: Ensure the picker starts with the value already in the HTML
      defaultDate: dateValueEl ? dateValueEl.textContent.trim() : null,
    });
    dataMapMoObj.dateVal = block
      .querySelector(".start-date-value")
      .textContent.trim();
    // 3. Click event for all browsers (including Safari)
    wrapperEl.addEventListener("click", (e) => {
      e.preventDefault();

      // The Safari/Firefox Fix: Manually focus internal input
      if (fp && fp._input) {
        fp._input.focus();
      }

      fp.open();
      if (wrapperEl.classList.contains("start-date-wrap")) {
        return block.querySelector(".start-date").append(fp.calendarContainer);
      }
      return e;
    });
  };
  // Initialize your specific structure
  initDatePicker(document.querySelector(".start-date-wrap"));
};

dataMapMoObj.syncMobileView = (block, textValue) => {
  // 1. Get all labels in the filter area (Month, Year, and Sort labels)
  const allLabels = block.querySelectorAll(
    ".cmmn-label, .period-label, .sort-label",
  );

  allLabels.forEach((labelinn) => {
    // 2. Compare the text of the label with the value clicked on desktop
    if (labelinn.textContent.trim() === textValue) {
      // 3. Get the ID from the 'for' attribute to find the input
      const radioId = labelinn.getAttribute("for");
      const radioInput = document.getElementById(radioId);

      if (radioInput) {
        // 4. Set the radio to checked
        radioInput.checked = true;

        // 5. Manually trigger a 'change' event so your filter logic knows to run
        radioInput.dispatchEvent(new Event("change", { bubbles: true }));
      }
    }
  });
};

dataMapMoObj.getSelectedFilters = (block) => {
  // 1. Capture the checked radio inputs from each group
  const selectedMonthRadio = block.querySelector(
    'input[name="mobile-month"]:checked',
  );
  const selectedYearRadio = block.querySelector(
    'input[name="mobile-year"]:checked',
  );
  const selectedSortRadio = block.querySelector('input[name="sort"]:checked');
  const selectedCategoryAnchor = block.querySelector(
    '.ctgry-field[aria-current="page"]',
  );

  // 2. Extract values (using IDs for keys and Label Text for display values)
  const monthValue = selectedMonthRadio
    ? selectedMonthRadio?.nextElementSibling?.textContent.trim()
    : null;

  const yearLabel = block.querySelector(
    `label[for="${selectedYearRadio?.id}"]`,
  );
  const yearValue = yearLabel ? yearLabel.textContent.trim() : null;

  const sortLabel = block.querySelector(
    `label[for="${selectedSortRadio?.id}"]`,
  );
  const sortValue = sortLabel ? sortLabel.textContent.trim() : null;

  // For Category: Use label textContent to match your requirement
  const categoryValue =
    dataMapMoObj.selval ||
    (selectedCategoryAnchor ? selectedCategoryAnchor.textContent.trim() : null);

  return {
    category: categoryValue, // e.g., "Scheme Information Document (SID)"
    month: monthValue === "fab" ? "feb" : monthValue,
    year: yearValue,
    sort: sortValue,
  };
};

dataMapMoObj.formattitle = (fileName) => {
  if (!fileName) return "";

  return fileName
    .replace(/\.[^/.]+$/, "") // 1. Remove file extension
    .replace(/[-_]/g, " ") // 2. Replace BOTH hyphens and underscores with spaces
    .split(" ") // 3. Split into words
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
  // 5. Join back with spaces
};

dataMapMoObj.formatDatecf = (dateStr) => {
  const [day, month, year] = dateStr.split("-");

  // Create a date object (Note: Month is 0-indexed in JS Date constructor)
  const dateObj = new Date(year, month - 1, day);

  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(dateObj);
};

/**
 * Groups Scheme Summary Document results by folder name.
 * Files in the same folder (e.g., motilal-oswal-digital-india-fund/)
 * are grouped into a single card entry.
 * @param {Array} results - Array of result objects with path, title, publishDate
 * @returns {Array} Array of grouped objects: { folderName, title, publishDate, files: [{path, fileType, icon}] }
 */
dataMapMoObj.groupByFolder = (results) => {
  const folderMap = {};

  results.forEach((resp) => {
    const { path } = resp;
    // Extract folder name from path like:
    // /content/dam/motilal-mf/downloads/mf/scheme-summary-document/folder-name/file.ext
    const pathParts = path.split("/");
    // folder name is the second-to-last segment
    const folderName = pathParts[pathParts.length - 2] || "";

    if (!folderMap[folderName]) {
      folderMap[folderName] = {
        folderName,
        title: resp.title,
        publishDate: resp.publishDate !== "" ? resp.publishDate : "",
        files: [],
      };
    }

    // Determine file type and icon
    let icon;
    let fileType;
    const lowerPath = path.toLowerCase();
    if (lowerPath.endsWith(".xml")) {
      icon = "../../icons/file-xml.svg";
      fileType = "xml";
    } else if (lowerPath.endsWith(".xls") || lowerPath.endsWith(".xlsx")) {
      icon = "../../icons/file-xlsx.svg";
      fileType = "xlsx";
    } else {
      icon = "../../icons/file-pdf.svg";
      fileType = "pdf";
    }

    folderMap[folderName].files.push({ path, fileType, icon });

    // Keep the latest publishDate for the card
    const existingDate =
      folderMap[folderName].publishDate !== ""
        ? new Date(
          folderMap[folderName].publishDate.split("-").reverse().join("-"),
        )
        : "";
    const currentDate =
      resp.publishDate !== ""
        ? new Date(resp.publishDate.split("-").reverse().join("-"))
        : "";
    if (
      existingDate !== "" &&
      currentDate !== "" &&
      currentDate > existingDate
    ) {
      folderMap[folderName].publishDate = resp.publishDate;
    }
  });

  return Object.values(folderMap);
};

/**
 * Renders grouped Scheme Summary Document cards.
 * One card per folder, with download icons for each file type.
 * @param {Array} resultArr - Array of result objects from API
 * @returns {string} HTML string of grouped cards
 */
dataMapMoObj.renderSchemeSummaryCards = (resultArr) => {
  const grouped = dataMapMoObj.groupByFolder(resultArr);

  return grouped
    .map((group) => {
      // Format the folder name as the card title
      let title = dataMapMoObj.formattitle(group.folderName);
      const formattedDate =
        group.publishDate !== ""
          ? dataMapMoObj.formatDatecf(group.publishDate)
          : "";

      const pattern = new RegExp(`\\b(sid(?!dh\\b)|${smallcase.join("|")})\\b`, "gi");
      title = title.replace(pattern, (match) => match.toUpperCase());

      // Build download icons for each file type in the folder (order: PDF → XML → XLSX)
      const fileTypeOrder = { pdf: 1, xml: 2, xlsx: 3 };
      const sortedFiles = [...group.files].sort(
        (a, b) =>
          (fileTypeOrder[a.fileType] || 99) - (fileTypeOrder[b.fileType] || 99),
      );
      const fileIconsHTML = sortedFiles
        .map(
          (file) => `
              <a class="anchorimg anchorimg-${file.fileType}" href="${file.path}" title="Download ${file.fileType.toUpperCase()}">
                <img class="pdf-img" src="${file.icon}" alt="${title} ${file.fileType}">
              </a>`,
        )
        .join("");

      return `
            <div class="pdf-list">
                <div class="pdf-content">
                    <h3 class="pdf-title">
                      <span class="anchortitle">${title}</span>
                    </h3>
                    <div class="pdf-desc">
                        <span class="date-ctgry">${formattedDate}</span>
                        <span class="date-ctgry">${dataMapMoObj.dataskill[dataMapMoObj.selval]}/${dataMapMoObj.selval}</span>
                    </div>
                </div>
                <div class="pdf-icon pdf-icon-group">
                    ${fileIconsHTML}
                </div>
            </div>`;
    })
    .join("");
};

dataMapMoObj.keyval = {
  "Scheme Information Document (SID)": "sid",
  "Key Information Memorandum (KIM)": "key information memorandum",
  "SID Related Documents": "sid related documents",
  "Scheme Summary Documents": "scheme summary document",
  // 'document disclosure', // Mapping to your list, no sure
  "Addendum/Notice": "addendums",
  SAI: "sai",
  Financials: "financials",
  "Fact Sheets": "factsheet",
  "Scheme Portfolio Details": "month end portfolio", // Not Sure
  "Month End Scheme Performance": "month-end-scheme-performance",
  "Fundamental Attributes": "fundamental attributes section",
  "Valuation Policy": "valuation policy", // Not Sure
  "Debt & Money Market Transactions":
    "debt%20%26%20money%20market%20securities%20transactions",
  "Status of Redressal": "status of redressal",
  "Regulatory Updates": "regulatory updates",
  Presentations: "presentations",
  "Leaflets / Brochures": "leaflets/brochures",
  Forms: "forms",
  "Unclaimed Dividend / Redemption": "unclaimed dividend redemption",
  "Monthly Communique": "monthly communique", // Not there in UI
  "Total Expense Ratio": "total-expense-ratio", // Not there in UI
  Policies: "policies", // Not there in UI
  "AMFI IAP": "",
  "KYC & Redressal of Complaints": "",
  "Guidelines for Transmission of Units (AMFI Circular No. 110)": "",
  Remunerations: "",
  "Risk Adjusted Returns - Information Ratio (IR)": "",
  "Document Disclosure": "document disclosure",
  "Grievance Redressal Mechanism": "",
  '(SOP) for Centralized Mechanism for Reporting the Demise of an Investor': 'sop for centralized mechanism for reporting the demise of an investor',
  '(SOP) for Centralised Mechanism for Reporting the Demise of an Investor': 'sop for centralised mechanism for reporting the demise of an investor',
  'Disclosure of Empanelment Details of Mutual Fund Distributors': 'disclosure of empanelment details of mutual fund distributors',
  'Disclosure of Empanelment Details of PMS Distributors': 'disclosure of empanelment details of pms distributors',
  "Ease of Doing Investment and Ease of Doing Business – Simplification and Standardisation of the framework for Transmission of Securities": "ease of doing investment and ease of doing business – simplification and standardisation of the framework for transmission of securities",
  "IDCW History": 'idcw history',
  // Scheme Summary Documents: '',
};
dataMapMoObj.keyvalurl = {
  sid: "Scheme Information Document (SID)",
  "key-information-memorandum": "Key Information Memorandum (KIM)",
  "sid-related-documents": "SID Related Documents",
  "scheme-summary-documents": "Scheme Summary Documents",
  // 'document disclosure', // Mapping to your list, no sure
  addendums: "Addendum/Notice",
  sai: "SAI",
  financials: "Financials",
  factsheets: "Fact Sheets",
  "scheme-portfolio-details": "Scheme Portfolio Details", // Not Sure
  "month-end-scheme-performance": "Month End Scheme Performance",
  "fundamental-attributes": "Fundamental Attributes",
  "valuation-policy": "Valuation Policy", // Not Sure
  "debt-money-market-securities-transactions":
    "Debt & Money Market Transactions",
  "status-of-redressal": "Status of Redressal",
  "regulatory-updates": "Regulatory Updates",
  presentations: "Presentations",
  "leaflets-brochures": "Leaflets / Brochures",
  forms: "Forms",
  "unclaimed-dividend-redemption": "Unclaimed Dividend / Redemption",
  "monthly-communique": "Monthly Communique", // Not there in UI
  "Total Expense Ratio": "total-expense-ratio", // Not there in UI
  policies: "Policies", // Not there in UI
  "amfi-lap": "AMFI IAP",
  "kyc-and-redressal-of-complaints": "KYC & Redressal of Complaints",
  "guidelines-for-transmission-of-units-procedure-amfi-circular-no-110":
    "Guidelines for Transmission of Units (AMFI Circular No. 110)",
  remunerations: "Remunerations",
  "risk-adjusted-return": "Risk Adjusted Returns - Information Ratio (IR)",
  "document-disclosure": "Document Disclosure",
  "grievance-redressal-mechanism": "Grievance Redressal Mechanism",
  'sop-for-centralized-mechanism-for-reporting-the-demise-of-an-investor': '(SOP) for Centralized Mechanism for Reporting the Demise of an Investor',
  'sop-for-centralised-mechanism-for-reporting-the-demise-of-an-investor': '(SOP) for Centralised Mechanism for Reporting the Demise of an Investor',
  'disclosure-of-empanelment-details-of-mutual-fund-distributors': 'Disclosure of Empanelment Details of Mutual Fund Distributors',
  'disclosure-of-empanelment-details-of-pms-distributors': 'Disclosure of Empanelment Details of PMS Distributors',
  'ease-of-doing-investment-and-ease-of-doing-business-simplification-and-standardisation-of-the-framework-for-transmission-of-securities': 'Ease of Doing Investment and Ease of Doing Business – Simplification and Standardisation of the framework for Transmission of Securities',
  'idcw-history': 'IDCW History'
  // Scheme Summary Documents: '',
};
dataMapMoObj.dataskill = {
  "Scheme Information Document (SID)": "Scheme Documents",
  "Scheme Information Document": "Scheme Documents",
  "Key Information Memorandum (KIM)": "Scheme Documents",
  "Key Information Memorandum": "Scheme Documents",
  "SID Related Documents": "Scheme Documents",
  "Scheme Summary Documents": "Scheme Documents",
  // 'document-disclosure', // Mapping to your list, no sure
  "Addendum/Notice": "Scheme Documents",
  SAI: "Scheme Documents",
  Financials: "Reports & Disclosures",
  "Fact Sheets": "Reports & Disclosures",
  "Scheme Portfolio Details": "Reports & Disclosures", // Not Sure
  "Month End Scheme Performance": "Reports & Disclosures",
  "Fundamental Attributes": "Reports & Disclosures",
  "Valuation Policy": "Reports & Disclosures", // Not Sure
  "Debt & Money Market Transactions": "Reports & Disclosures",
  "Status of Redressal": "Reports & Disclosures",
  "Risk Adjusted Returns - Information Ratio (IR)": "Reports & Disclosures",
  "Regulatory Updates": "Reports & Disclosures",
  "AMFI IAP": "Reports & Disclosures",
  Presentations: "Investor Communication",
  "Leaflets / Brochures": "Investor Communication",
  "Leaflets/Brochures": "Investor Communication",
  Forms: "Forms",
  "KYC & Redressal of Complaints": "Forms",
  "Guidelines for Transmission of Units (AMFI Circular No. 110)": "Forms",
  "Unclaimed Dividend / Redemption": "Investor Protection",
  "Monthly Communique": "Investor Communication", // Not there in UI
  "Total Expense Ratio": "total-expense-ratio", // Not there in UI
  Policies: "Reports & Disclosures", // Not there in UI
  Remunerations: "",
  "Document Disclosure": "Reports & Disclosures",
  "Grievance Redressal Mechanism": "Investor Protection",
  '(SOP) for Centralized Mechanism for Reporting the Demise of an Investor': 'Forms',
  '(SOP) for Centralised Mechanism for Reporting the Demise of an Investor': 'Forms',
  'Disclosure of Empanelment Details of PMS Distributors': "Reports & Disclosures",
  'Disclosure of Empanelment Details of Mutual Fund Distributors': "Reports & Disclosures",
  "Ease of Doing Investment and Ease of Doing Business – Simplification and Standardisation of the framework for Transmission of Securities": "Forms",
  "IDCW History": "Reports & Disclosures",
};
dataMapMoObj.keyvaldrop = {
  "Scheme Information Document (SID)": "sid",
  "Key Information Memorandum (KIM)": "key-information-memorandum",
  "SID Related Documents": "sid-related-documents",
  "Scheme Summary Documents": "scheme-summary-document",
  // 'document-disclosure', // Mapping to your list, no sure
  "Addendum/Notice": "addendums",
  SAI: "sai",
  Financials: "financials",
  "Fact Sheets": "factsheet",
  "Scheme Portfolio Details": "month-end-portfolio", // Not Sure
  "Month End Scheme Performance": "month-end-scheme-performance",
  "Fundamental Attributes": "fundamental-attributes-section",
  "Valuation Policy": "valuation-policy", // Not Sure
  "Debt & Money Market Transactions":
    "debt-money-market-securities-transactions",
  "Status of Redressal": "status-of-redressal",
  "Regulatory Updates": "regulatory-updates",
  Presentations: "presentations",
  "Leaflets / Brochures": "leafletsbrochures",
  Forms: "forms",
  "Unclaimed Dividend / Redemption": "unclaimed-dividend-redemption",
  "Monthly Communique": "monthly-communique", // Not there in UI
  "Total Expense Ratio": "total-expense-ratio", // Not there in UI
  Policies: "policies", // Not there in UI
  "AMFI IAP": "",
  "KYC & Redressal of Complaints": "",
  "Guidelines for Transmission of Units (AMFI Circular No. 110)": "",
  Remunerations: "",
  "Risk Adjusted Returns - Information Ratio (IR)": "",
  "Document Disclosure": "document-disclosure",
  "Grievance Redressal Mechanism": "",
  "Monthly Communique": "monthly-communique",
  '(SOP) for Centralized Mechanism for Reporting the Demise of an Investor': 'sop-for-centralized-mechanism-for-reporting-the-demise-of-an-investor',
  '(SOP) for Centralised Mechanism for Reporting the Demise of an Investor': 'sop-for-centralised-mechanism-for-reporting-the-demise-of-an-investor',
  'Disclosure of Empanelment Details of Mutual Fund Distributors': 'disclosure-of-empanelment-details-of-mutual-fund-distributors',
  'Disclosure of Empanelment Details of PMS Distributors': 'disclosure-of-empanelment-details-of-pms-distributors',
  'Ease of Doing Investment and Ease of Doing Business – Simplification and Standardisation of the framework for Transmission of Securities': 'ease-of-doing-investment-and-ease-of-doing-business–simplification-and-standardisation-of-the-framework-for-transmission-of-securities',
  "IDCW History": 'idcw-history'
  // Scheme Summary Documents: '',
};
dataMapMoObj.monthLookup = {
  jan: "January",
  feb: "February",
  mar: "March",
  apr: "April",
  may: "May",
  jun: "June",
  jul: "July",
  aug: "August",
  sep: "September",
  oct: "October",
  nov: "November",
  dec: "December",
};

dataMapMoObj.renderdrop = (block) => {
  // --- DESKTOP LOGIC ---
  const yearContainer = block
    .querySelector("#year-label")
    .closest(".smy-drpdwn-wrap");
  const yearMenu = yearContainer.querySelector(".drpdwn-menu");
  const yearLabel = yearContainer.querySelector(".drpdwn-sltxt");

  const selval = dataMapMoObj.keyvaldrop[dataMapMoObj.selval];
  if (selval !== "" && dataMapMoObj.dropdown[selval] !== undefined) {
    const yeardrop = dataMapMoObj.dropdown[selval];

    dataMapMoObj.sortedKeys = Object.keys(yeardrop).sort((a, b) => b - a);
    const initialYear = dataMapMoObj.sortedKeys[0];

    // Render Desktop Years
    yearMenu.innerHTML = dataMapMoObj.sortedKeys
      .map(
        (yr) =>
          `<button class="smy-drpdwn-list drpdwn-list" type="button">${yr}</button>`,
      )
      .join("");
    // yearLabel.textContent = initialYear;

    // --- MOBILE LOGIC: YEARS ---
    const mobileYearBody = block.querySelector(
      ".period-filter .accordion-field:nth-child(2) .accordion-body",
    );
    if (mobileYearBody) {
      mobileYearBody.innerHTML = dataMapMoObj.sortedKeys
        .map(
          (yr, index) => `
      <div class="period-field cmmn-field">
        <input class="period-inp cmmn-inp" type="radio" id="m-year-${yr}" name="mobile-year" ${yr === initialYear ? "checked" : ""}>
        <label class="period-label cmmn-label" for="m-year-${yr}">${yr}</label>
      </div>
    `,
        )
        .join("");
    }

    // --- DESKTOP LOGIC: MONTHS ---
    const monthContainer = block
      .querySelector("#month-label")
      .closest(".smy-drpdwn-wrap");
    const monthMenu = monthContainer.querySelector(".drpdwn-menu");
    const monthLabel = monthContainer.querySelector(".drpdwn-sltxt");
    let monthsArr = yeardrop[initialYear];
    if (monthsArr === undefined) {
      monthsArr = [];
    }
    const monthOrder = [
      "jan",
      "feb",
      "mar",
      "apr",
      "may",
      "jun",
      "jul",
      "aug",
      "sep",
      "oct",
      "nov",
      "dec",
    ];

    monthsArr.sort((a, b) => monthOrder.indexOf(a) - monthOrder.indexOf(b));
    // Filter out undefined/null/invalid months
    monthsArr = monthsArr.filter((m) => m && dataMapMoObj.monthLookup[m]);
    const initialMonthShort = monthsArr[0];
    const initialMonthFull = dataMapMoObj.monthLookup[initialMonthShort];

    monthMenu.innerHTML = monthsArr
      .map(
        (m) =>
          `<button class="smy-drpdwn-list drpdwn-list" type="button" data-short="${m}">${dataMapMoObj.monthLookup[m]}</button>`,
      )
      .join("");
    // monthLabel.textContent = initialMonthFull;

    // --- MOBILE LOGIC: MONTHS ---
    const mobileMonthBody = block.querySelector(
      ".period-filter .accordion-field:nth-child(1) .accordion-body",
    );
    if (mobileMonthBody) {
      mobileMonthBody.innerHTML = monthsArr
        .map(
          (m) => `
      <div class="period-field cmmn-field">
        <input class="period-inp cmmn-inp" type="radio" id="m-month-${m}" name="mobile-month" ${m === initialMonthShort ? "checked" : ""}>
        <label class="period-label cmmn-label" for="m-month-${m}">${dataMapMoObj.monthLookup[m]}</label>
      </div>
    `,
        )
        .join("");
    }

    // Update Params
    if (dataMapMoObj.param.year === "" && dataMapMoObj.param.month === "") {
      dataMapMoObj.param.year = dataMapMoObj.getVal("#year-label");
      dataMapMoObj.param.month = dataMapMoObj
        .getVal("#month-label")
        .slice(0, 3)
        .toLowerCase();

      if (
        dataMapMoObj.dropEvent === "" &&
        dataMapMoObj.selval !==
        "Risk Adjusted Returns - Information Ratio (IR)" &&
        dataMapMoObj.param.year !== "" &&
        dataMapMoObj.param.month !== ""
      ) {
        dataMapMoObj.categoryfilter(block, dataMapMoObj.param);
      } else if (
        dataMapMoObj.selval !== "Risk Adjusted Returns - Information Ratio (IR)"
      ) {
        dataMapMoObj.categoryfilter(block, dataMapMoObj.param);
      }
    }

    // dataMapMoObj.param.month = initialMonthShort;
    // dataMapMoObj.param.year = initialYear;
  }
};

dataMapMoObj.dropdownload = (block) => {
  getDownloadsDropdownOptions(dataMapMoObj.param.type)
    .then((result) => {
      dataMapMoObj.dropdown = result;
      dataMapMoObj.renderdrop(block);
    })
    .catch((error) => console.error(error));
};

dataMapMoObj.findMapping = function (respCategory) {
  // 1. Get the formatted version of the incoming category
  const target = this.formattitle(respCategory).trim();

  // 2. Iterate through the mapping object keys
  const keys = Object.keys(this.dataskill);
  for (const key of keys) {
    // Compare formatted key vs formatted target (case-insensitive)
    if (key.trim().toLowerCase() === target.toLowerCase()) {
      return this.dataskill[key];
    }
  }

  // 3. Fallback: if no match is found, return the formatted title
  // so it doesn't show "undefined"
  return target;
};

dataMapMoObj.sortrender = (block, param) => {
  const pdfContainer = block.querySelector(".pdf-container .pdf-list-content");

  // 2. Clear container once
  pdfContainer.innerHTML = "";
  if (block.querySelector(".download-pagination-footer")) {
    block.querySelector(".download-pagination-footer").remove();
  }
  try {
    const sortResults = (data, direction = "newest") =>
      [...data].sort((asort, bsort) => {
        // Standardizing "DD-MM-YYYY" to "YYYY-MM-DD" for Date parsing
        const dateA = new Date(
          asort.publishDate.split("-").reverse().join("-"),
        );
        const dateB = new Date(
          bsort.publishDate.split("-").reverse().join("-"),
        );

        if (direction === "newest") {
          return dateB - dateA; // High to Low (Dec 2024 -> Jan 2024)
        }
        return dateA - dateB; // Low to High (Jan 2024 -> Dec 2024)
      });

    let resultArr = [];

    // Apply the sorting based on the parameter
    if (param.sort === "Latest" || param.sort === "Newest to Oldest") {
      // resultArr = sortResults(dataMapMoObj.results, 'newest');
      dataMapMoObj.param.year = "";
      dataMapMoObj.param.month = "";
      block
        .querySelector("#month-label")
        .closest(".cmmn-drpdwn-wrap")
        .querySelector(".drpdwn-sltxt").textContent = "";
      block
        .querySelector("#year-label")
        .closest(".cmmn-drpdwn-wrap")
        .querySelector(".drpdwn-sltxt").textContent = "";
      block
        .querySelectorAll(".period-filter .period-inp")
        .forEach((el) => (el.checked = false));
      dataMapMoObj.categoryfilter(block, dataMapMoObj.param);

      return false;
    }
    if (param.sort === "Oldest to Newest") {
      // resultArr = sortResults(dataMapMoObj.results, 'oldest');
      dataMapMoObj.param.month = "";
      dataMapMoObj.param.year = "";
      block
        .querySelector("#month-label")
        .closest(".cmmn-drpdwn-wrap")
        .querySelector(".drpdwn-sltxt").textContent = "";
      block
        .querySelector("#year-label")
        .closest(".cmmn-drpdwn-wrap")
        .querySelector(".drpdwn-sltxt").textContent = "";
      block
        .querySelectorAll(".period-filter .period-inp")
        .forEach((el) => (el.checked = false));
      dataMapMoObj.categoryfilter(block, dataMapMoObj.param);
      return false;
    }
    // Default fallback
    resultArr = dataMapMoObj.results;

    // Use grouped card rendering for Scheme Summary Documents
    let pdfListHTML;
    if (dataMapMoObj.selval === "Scheme Summary Documents") {
      pdfListHTML = dataMapMoObj.renderSchemeSummaryCards(resultArr);
    } else {
      pdfListHTML = resultArr
        .map((resp) => {
          // Format data before injection
          let title = dataMapMoObj.formattitle(resp.title);
          const formattedDate =
            resp.publishDate !== ""
              ? dataMapMoObj.formatDatecf(resp.publishDate)
              : "";
          const { path } = resp;
          let icon;
          let fileType;
          if (path.includes(".xls")) {
            icon = "../../icons/file-xlsx.svg";
            fileType = "xlsx";
          } else {
            icon = "../../icons/pdf-icon.svg";
            fileType = "pdf";
          }
          const pattern = new RegExp(
            `\\b(sid(?!dh\\b)|${smallcase.join("|")})\\b`,
            "gi",
          );
          title = title.replace(pattern, (match) => {
            return match.toUpperCase();
          });
          // Use a template literal to build the string
          return `
          <div class="pdf-list">
              <div class="pdf-content">
                  <h3 class="pdf-title">
                    <a class= "anchortitle">${title}</a>
                  </h3>
                  <div class="pdf-desc">
                      <span class="date-ctgry">${formattedDate}</span>
                      <span class="date-ctgry">${dataMapMoObj.findMapping(resp.category)}/${dataMapMoObj.formattitle(resp.category)}</span>
                  </div>
              </div>
              <div class="pdf-icon">
                  <a class= "anchorimg" href="${path}">
                    <img class="pdf-img" src="${icon}" alt="${title} ${fileType}">
                  </a>
              </div>
          </div>`;
        })
        .join("");
    }

    // 4. Update the DOM exactly once
    pdfContainer.innerHTML = pdfListHTML;
    block.querySelector(".pdf-container").classList.add("active");
    const items = Array.from(
      block.querySelectorAll(".pdf-container .pdf-list"),
    );
    const itemsPerPage = items.slice(0, 9).length;
    if (items.length > itemsPerPage) {
      dataMapMoObj.setupPagination(block, items, itemsPerPage);
    }
    pdfContainer.addEventListener("click", (e) => {
      // Skip for Scheme Summary Documents - popup handles downloads
      if (dataMapMoObj.selval === "Scheme Summary Documents") return;
      const link = e.target.closest(".anchortitle, .anchorimg");

      if (link) {
        const url = link.getAttribute("href");

        if (url && url.toLowerCase().endsWith(".pdf")) {
          e.preventDefault();
          const fileName = url.split("/").pop();
          dataMapMoObj.handleDownload(url, fileName);
        }
      }
    });
    dataMapMoObj.handleDownload = (url, fileName) => {
      fetch(url)
        .then((response) => {
          if (!response.ok) throw new Error("Network error");
          return response.blob();
        })
        .then((blob) => {
          const blobUrl = window.URL.createObjectURL(blob);
          const alink = document.createElement("a");

          // Critical: Set these attributes for iOS compatibility
          alink.style.display = "none";
          alink.href = blobUrl;
          alink.download = fileName;
          alink.target = "_blank"; // Helpful for mobile Safari fallback

          document.body.appendChild(alink); // FIXED: was 'a', now 'alink'
          alink.click();

          // Cleanup
          setTimeout(() => {
            window.URL.revokeObjectURL(blobUrl);
            alink.remove();
          }, 100);
        })
        .catch((err) => {
          console.error("Download failed, falling back:", err);
          // Fallback: Open in new tab if Fetch/CORS fails
          window.open(url, "_blank");
        });
    };
  } catch (error) {
  }
};
dataMapMoObj.keyToHeader = {
  schemeName: "Scheme Name",
  benchmarkName: "Benchmark",
  schemeRisk: "Riskometer Scheme",
  benchmarkRisk: "Riskometer Benchmark",
  navRecdt: "NAV Date",
  regularNav: "NAV Regular",
  directNav: "NAV Direct",
  "1yrregular": "Return 1 Year (%) Regular",
  "1yrdirect": "Return 1 Year (%) Direct",
  "1yrbm": "Return 1 Year (%) Benchmark",
  "1yrirregular": "Information Ratio* 1 Year (Regular)",
  "1yrirdirect": "Information Ratio* 1 Year (Direct)",
  "3yrregular": "Return 3 Year (%) Regular",
  "3yrdirect": "Return 3 Year (%) Direct",
  "3yrbm": "Return 3 Year (%) Benchmark",
  "3yrirregular": "Information Ratio* 3 Year (Regular)",
  "3yrirdirect": "Information Ratio* 3 Year (Direct)",
  "5yrregular": "Return 5 Year (%) Regular",
  "5yrdirect": "Return 5 Year (%) Direct",
  "5yrbm": "Return 5 Year (%) Benchmark",
  "5yrirregular": "Information Ratio* 5 Year (Regular)",
  "5yrirdirect": "Information Ratio* 5 Year (Direct)",
  "10yrregular": "Return 10 Year (%) Regular",
  "10yrdirect": "Return 10 Year (%) Direct",
  "10yrbm": "Return 10 Year (%) Benchmark",
  "10yrirregular": "Information Ratio* 10 Year (Regular)",
  "10yrirdirect": "Information Ratio* 10 Year (Direct)",
  siregular: "Return since launch (%) Regular",
  sidirect: "Return since launch (%) Direct",
  sibm: "Return since launch (%) Benchmark",
  dailyaum: "Daily AUM (Cr.)",
};

dataMapMoObj.riskAdjustment = async (block) => {
  dataMapMoObj.toggleLoaderSpinner(
    block.querySelector(".filtered-content"),
    true,
  );
  const riskupper = block.querySelector(".upper-filter");
  riskupper.classList.add("risk-return-active");
  Array.from(block.querySelector(".filtered-content").children).forEach(
    (elem) => {
      elem.classList.remove("active");
    },
  );
  try {
    let lasteddata;
    // block.querySelector('.filtered-content .table-container').classList.add('active');
    block
      .querySelector(".filter-content .sticky-fields")
      .classList.add("risk-return-active");
    if (
      dataMapMoObj.selectTab !== "HistoricalDate" ||
      dataMapMoObj.selectTab === undefined
    ) {
      const reqObj = {
        latestData: true,
      };
      lasteddata = await getRiskReturns(reqObj);
      // 'https://www.motilaloswalmf.com/mutualfund/api/v1/getriskreturns'
      // https://www.motilaloswalmf.com/mutualfund/api/v1/getriskreturns
      // console.log(lasteddata?.data);
      const dataResp = lasteddata?.data;
      // console.log(dataResp.data);
      const tabsel =
        dataMapMoObj.selectTab === undefined
          ? "latest"
          : dataMapMoObj.selectTab;
      dataMapMoObj.renderTable(block, dataResp, tabsel.toLowerCase());
      dataMapMoObj.toggleLoaderSpinner(
        block.querySelector(".filtered-content"),
        false,
      );
    }
    if (dataMapMoObj.selectTab === "HistoricalDate") {
      // const dataResp = dataMapMoObj.latestdata;
      // console.log(dataResp.data);
      // dataMapMoObj.renderTable(block, dataResp.data, 'historical');
      const reqObj = {
        selectedDate: dataMapMoObj.dateVal.split("/").reverse().join("-"),
      };
      lasteddata = await getRiskReturns(reqObj);
      // console.log(lasteddata?.data);
      const datav2 = lasteddata?.data;
      // console.log(datav2);
      dataMapMoObj.renderTable(block, datav2, "historical");
      dataMapMoObj.toggleLoaderSpinner(
        block.querySelector(".filtered-content"),
        false,
      );
    }
  } catch (error) {
    dataMapMoObj.toggleLoaderSpinner(
      block.querySelector(".filtered-content"),
      false,
    );
    Array.from(block.querySelector(".filtered-content").children).forEach(
      (elem) => {
        elem.classList.remove("active");
      },
    );
    block
      .querySelector(".filtered-content .no-docs-container")
      .classList.add("active");
  }
};

const getDynamicFileName = (block) => {
  const tbody = block.querySelector(".tbl-tbody");
  const rows = tbody ? tbody.querySelectorAll(".tbl-tbody-tr") : [];

  // Get the category dropdown selection
  const categoryBtn = block
    .querySelector("#fund-category")
    ?.closest(".cmmn-drpdwn-wrap")
    ?.querySelector(".drpdwn-sltxt");
  const selectedCategory = categoryBtn ? categoryBtn.textContent.trim() : "All";

  let baseName = "FundDetail";

  if (rows.length === 1) {
    // Case 1: Single row - use the scheme name from the first cell
    const schemeName = rows[0]
      .querySelector(".tbl-tbody-td")
      ?.textContent.trim();
    if (schemeName) baseName = schemeName;
  } else if (selectedCategory !== "All") {
    // Case 2: Multiple rows - use the selected category name
    baseName = selectedCategory;
  }

  // Sanitize filename (remove special characters not allowed in file names)
  const sanitizedName = baseName.replace(/[/\\?%*:|"<>]/g, "-");

  // Append Timestamp for uniqueness
  const timestamp = new Date().getTime();
  return `${sanitizedName}_${timestamp}.csv`;
};

const exportTableToCSV = (block) => {
  const table = block.querySelector(".table-content");
  if (!table) return;

  let csvContent = "";
  const rows = table.querySelectorAll("tr");

  rows.forEach((row) => {
    const rowData = [];
    const cells = row.querySelectorAll("th, td");
    cells.forEach((cell) => {
      let text = cell.textContent.trim();
      text = `"${text.replace(/"/g, '""')}"`;
      rowData.push(text);
    });
    csvContent += `${rowData.join(",")}\r\n`;
  });

  const fileName = getDynamicFileName(block);
  const blob = new Blob([`\uFEFF${csvContent}`], {
    type: "text/csv;charset=utf-8;",
  });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");

  // Safari-friendly download trigger
  if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, fileName);
  } else {
    link.href = url;
    link.setAttribute("download", fileName);
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  setTimeout(() => URL.revokeObjectURL(url), 100);
};

const initXlsxDownload = (block) => {
  const downloadBtn = block.querySelector(".xlsx-btn");
  if (downloadBtn && downloadBtn.dataset.xlsxBound !== "true") {
    // renderTable (and therefore initXlsxDownload) runs on every data load,
    // tab switch and filter change. The .xlsx-btn is a persistent element, so
    // guard against attaching the click listener more than once -- otherwise a
    // single click fires one download per stacked listener.
    downloadBtn.dataset.xlsxBound = "true";
    downloadBtn.addEventListener("click", (e) => {
      e.preventDefault();
      exportTableToCSV(block);
    });
  }
};
dataMapMoObj.renderTable = (block, dataResp, param) => {
  /**
   * 1. DATA CONFIGURATION & STATE
   */
  const funds = [
    { label: "All", value: "all" },
    { label: "Multi Cap Fund", value: "MM" },
    { label: "Arbitrage Fund", value: "AR" },
    { label: "Balanced Advantage Fund", value: "DE" },
    { label: "Sectoral/Thematic Funds", value: "BC" },
    { label: "Sectoral/Thematic Funds", value: "DF" },
    { label: "ELSS", value: "LT" },
    { label: "Flexi Cap Fund", value: "CP" },
    { label: "Focused Fund", value: "MF" },
    { label: "Mid Cap Fund", value: "FM" },
    { label: "Sectoral/Thematic Funds", value: "IO" },
    { label: "Large & Mid Cap Fund", value: "LM" },
    { label: "Large Cap Fund", value: "LC" },
    { label: "Sectoral/Thematic Funds", value: "AM" },
    { label: "Sectoral/Thematic Funds", value: "MT" },
    { label: "Multi Asset Allocation Fund", value: "MA" },
    { label: "Sectoral/Thematic Funds", value: "MQ" },
    { label: "Small Cap Fund", value: "SC" },
  ];

  // The state object now tracks the active array from dataResp
  const state = {
    apiData: dataResp[param] || [],
    selectedCategory: "All",
    selectedScheme: "All",
  };

  /**
   * 2. FORMATTING & TABLE COMPONENTS
   */
  const getFormattedValue = (key, value) => {
    if (
      value === null ||
      value === undefined ||
      value === "" ||
      value === 0 ||
      value === "0.00"
    ) {
      return "0.00";
    }
    if (key === "navRecdt") {
      const date = new Date(value);
      return isNaN(date.getTime())
        ? "NA"
        : date.toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        });
    }
    const isReturnCol = /^(1yr|3yr|5yr|10yr|si)(regular|direct|bm)$/.test(key);
    if (isReturnCol) return `${value}%`;
    return value;
  };

  const internalRenderTable = (dataArray) => {
    const config = Object.entries(dataMapMoObj.keyToHeader);
    const tableEl = table({ class: "table-content" });
    const headerTr = tr({ class: "tbl-thead-tr" });

    config.forEach(([_, label]) => {
      headerTr.append(th({ class: "tbl-thead-th" }, label));
    });
    tableEl.append(thead({ class: "tbl-thead" }, headerTr));

    const tableBody = tbody({ class: "tbl-tbody" });
    dataArray.forEach((scheme) => {
      const row = tr({ class: "tbl-tbody-tr" });
      config.forEach(([key, _]) => {
        const finalValue = getFormattedValue(key, scheme[key]);
        row.append(td({ class: "tbl-tbody-td" }, finalValue));
      });
      tableBody.append(row);
    });

    tableEl.append(tableBody);
    return tableEl;
  };

  /**
   * 3. FILTERING & DROPDOWN UPDATES
   */
  const renderFilteredTable = () => {
    const codesForCategory = funds
      .filter((f) => f.label === state.selectedCategory)
      .map((f) => f.value);

    const filtered = state.apiData.filter((item) => {
      const matchCat =
        state.selectedCategory === "All" ||
        codesForCategory.includes(item.schemeCode);
      const matchScheme =
        state.selectedScheme === "All" ||
        item.schemeName === state.selectedScheme;
      return matchCat && matchScheme;
    });

    filtered.sort(
      (a, b) => new Date(a.dtofalotment) - new Date(b.dtofalotment),
    );

    const wrapper = block.querySelector(".table-wrapper");
    if (wrapper) {
      wrapper.innerHTML = "";
      wrapper.append(internalRenderTable(filtered));
    }
  };

  const updateSchemeDropdown = () => {
    const schemeContainer = block.querySelector("#scheme-category");
    if (!schemeContainer) return;
    const menu = schemeContainer.parentElement.querySelector(".drpdwn-menu");
    const displayBtn =
      schemeContainer.parentElement.querySelector(".drpdwn-sltxt");

    // YOUR FILTER LOGIC
    const validCodes = funds
      .filter(
        (f) =>
          state.selectedCategory === "All" ||
          f.label === state.selectedCategory,
      )
      .map((f) => f.value);

    const optionsMap = new Map();
    state.apiData.forEach((item) => {
      if (item.schemeName && validCodes.includes(item.schemeCode)) {
        const itemDate = new Date(item.dtofalotment);
        if (
          !optionsMap.has(item.schemeName) ||
          itemDate < optionsMap.get(item.schemeName).date
        ) {
          optionsMap.set(item.schemeName, {
            label: item.schemeName,
            date: itemDate,
          });
        }
      }
    });

    const sortedSchemes = Array.from(optionsMap.values()).sort(
      (a, b) => a.date - b.date,
    );

    // UPDATE DESKTOP MENU
    menu.innerHTML = `<button class="scheme-list drpdwn-list" type="button">All</button>${sortedSchemes
      .map(
        (s) =>
          `<button class="scheme-list drpdwn-list" type="button">${s.label}</button>`,
      )
      .join("")}`;

    // UPDATE MOBILE OVERLAY (Applying the same filter logic)
    const mobileSchemeBody = document.querySelector(".scheme-filter-body");
    if (mobileSchemeBody) {
      let mobileHTML = `
      <div class="scheme-field cmmn-field">
        <input class="scheme-inp cmmn-inp" type="radio" id="ms-all" name="scheme" ${state.selectedScheme === "All" ? "checked" : ""}>
        <label class="scheme-label cmmn-label" for="ms-all">All</label>
      </div>`;

      mobileHTML += sortedSchemes
        .map(
          (s, i) => `
      <div class="scheme-field cmmn-field">
        <input class="scheme-inp cmmn-inp" type="radio" id="ms-${i}" name="scheme" ${state.selectedScheme === s.label ? "checked" : ""}>
        <label class="scheme-label cmmn-label" for="ms-${i}">${s.label}</label>
      </div>
    `,
        )
        .join("");

      mobileSchemeBody.innerHTML = mobileHTML;
    }

    displayBtn.textContent = state.selectedScheme;
    attachDropdownEvents(menu, "scheme");
  };

  const renderCategoryDropdown = () => {
    const catContainer = block.querySelector("#fund-category");
    if (!catContainer) return;
    const menu = catContainer.parentElement.querySelector(".drpdwn-menu");
    const displayBtn =
      catContainer.parentElement.querySelector(".drpdwn-sltxt");

    const labels = [...new Set(funds.map((f) => f.label))]
      .filter((l) => l !== "All")
      .sort((a, b) => a.localeCompare(b));

    const allOptions = ["All", ...labels];

    // UPDATE DESKTOP
    menu.innerHTML = allOptions
      .map(
        (label) =>
          `<button class="scheme-list drpdwn-list" type="button">${label}</button>`,
      )
      .join("");

    // UPDATE MOBILE
    const mobileCatBody = document.querySelector(".fund-filter-body");
    if (mobileCatBody) {
      mobileCatBody.innerHTML = allOptions
        .map(
          (label, i) => `
      <div class="fund-field cmmn-field">
        <input class="fund-inp cmmn-inp" type="radio" id="m-cat-${i}" name="fundCtgry" ${state.selectedCategory === label ? "checked" : ""}>
        <label class="fund-label cmmn-label" for="m-cat-${i}">${label}</label>
      </div>
    `,
        )
        .join("");
    }

    displayBtn.textContent = state.selectedCategory;
    attachDropdownEvents(menu, "category");
  };

  const attachDropdownEvents = (menu, type) => {
    const container = menu.closest(".cmmn-select-drpdwn");
    const displayBtn = container.querySelector(".drpdwn-sltxt");

    menu.querySelectorAll(".drpdwn-list").forEach((btn) => {
      btn.onclick = (e) => {
        e.preventDefault();
        const val = btn.textContent.trim();
        displayBtn.textContent = val;

        // Close dropdown
        menu.classList.remove("active");
        container.classList.remove("active");

        if (type === "category") {
          state.selectedCategory = val;
          state.selectedScheme = "All"; // Reset Scheme state

          updateSchemeDropdown(); // Refresh Desktop Schemes

          // Sync Mobile Category Overlay
          const mobCatOverlay = block.querySelector(".fund-ctgry-overlay");
          dataMapMoObj.syncMobileView(mobCatOverlay, val);

          // Reset Mobile Scheme Overlay to "All"
          const mobSchemeOverlay = block.querySelector(".scheme-overlay");
          dataMapMoObj.syncMobileView(mobSchemeOverlay, val);
        } else {
          state.selectedScheme = val;

          // Sync Mobile Scheme Overlay
          const mobSchemeOverlay = block.querySelector(".scheme-overlay");
          dataMapMoObj.syncMobileView(mobSchemeOverlay, val);
        }

        renderFilteredTable(); // Final data update
      };
    });
  };

  document.addEventListener("change", (e) => {
    if (e.target.classList.contains("cmmn-inp")) {
      const label = document.querySelector(`label[for="${e.target.id}"]`);
      const val = label.textContent.trim();

      if (e.target.name === "fundCtgry") {
        state.selectedCategory = val;
        state.selectedScheme = "All"; // Reset scheme
        renderCategoryDropdown(); // Re-sync both UIs
        updateSchemeDropdown(); // Re-sync both UIs
      } else if (e.target.name === "scheme") {
        state.selectedScheme = val;
        updateSchemeDropdown(); // Re-sync both UIs
      }
      renderFilteredTable(); // Update the actual data list/table
    }
  });

  /**
   * 4. TAB SWITCH LOGIC
   */
  const initTabSwitch = () => {
    const tabButtons = block.querySelectorAll(
      ".ltst-hstcl-wrap .ltst-hstcl-btn",
    );
    const fundSchemeWrap = block.querySelector(".fund-scheme-wrap");

    tabButtons.forEach((btn) => {
      // 1. Remove any old listeners to prevent memory leaks/duplicate calls
      btn.removeEventListener("click", handleTabSelection);
      btn.addEventListener("click", handleTabSelection);
    });

    function handleTabSelection(event) {
      const btn = event.currentTarget;

      // 2. STOP if the tab is already active (Prevents redundant API calls)
      if (btn.classList.contains("active")) return;

      event.preventDefault();

      // UI: Toggle active class
      tabButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      // Identify selected tab
      const tabText = btn.textContent.trim(); // "Latest" or "Historical"
      const selectedTabKey = tabText.toLowerCase();

      // 3. Update State Logic
      dataMapMoObj.selectTab = tabText;
      state.selectedCategory = "All";
      state.selectedScheme = "All";
      state.apiData = dataResp[selectedTabKey] || [];

      // Sort new data
      state.apiData.sort((a, b) => new Date(b.navRecdt) - new Date(a.navRecdt));

      // 4. Handle Specific View Logic (Historical vs Latest)
      if (tabText === "Historical") {
        fundSchemeWrap?.classList.remove("hide-date");
        dataMapMoObj.selectTab = "HistoricalDate";
      } else {
        fundSchemeWrap?.classList.add("hide-date");
        dataMapMoObj.selectTab = "Latest";
      }

      // 5. Refresh UI components
      renderCategoryDropdown();
      updateSchemeDropdown();
      renderFilteredTable();

      // 6. SINGLE API CALL
      if (typeof dataMapMoObj.riskAdjustment === "function") {
        // console.log(`Fetching risk adjustment for: ${tabText}`);
        dataMapMoObj.riskAdjustment(block);
      }
    }
  };

  /**
   * 5. APP INITIALIZATION
   */
  state.apiData.sort((a, b) => new Date(b.navRecdt) - new Date(a.navRecdt));

  initTabSwitch(); // Initialize tabs
  renderCategoryDropdown();
  updateSchemeDropdown();
  renderFilteredTable();
  initXlsxDownload(block);
};
dataMapMoObj.categoryfilter = (block, param) => {
  dataMapMoObj.toggleLoaderSpinner(
    block.querySelector(".filtered-content"),
    true,
  );
  const arr = [
    "KYC & Redressal of Complaints",
    "Guidelines for Transmission of Units (AMFI Circular No. 110)",
    "Remunerations",
    "Risk Adjusted Returns - Information Ratio (IR)",
    "AMFI IAP",
    "Disclosure of Empanelment Details of Mutual Fund Distributors",
    "Disclosure of Empanelment Details of PMS Distributors"
  ];
  const isSummary = dataMapMoObj.selval === "Scheme Summary Documents";
  searchDownloadDocuments(param, isSummary)
    .then((result) => {
      // 1. Parse results safely
      if (!arr.includes(dataMapMoObj.selval)) {
        const responseData = typeof result === "string" ? JSON.parse(result) : result;
        const { results } = responseData;
        const pdfContainer = block.querySelector(
          ".pdf-container .pdf-list-content",
        );

        // 2. Clear container once
        pdfContainer.innerHTML = "";
        if (block.querySelector(".download-pagination-footer")) {
          block.querySelector(".download-pagination-footer").remove();
        }

        // 3. Map results to an array of strings and join them (Faster than innerHTML +=)
        Array.from(block.querySelector(".filtered-content").children).forEach(
          (elemchidl) => {
            elemchidl.classList.remove("active");
          },
        );
        block.querySelector(".no-docs-container").classList.remove("active");
        block.querySelector(".pdf-container").classList.remove("active");
        if (results.length !== 0) {
          dataMapMoObj.results = results;
          const sortResults = (data, direction = "newest") =>
            [...data].sort((a, b) => {
              // Standardizing "DD-MM-YYYY" to "YYYY-MM-DD" for Date parsing
              const dateA = new Date(
                a.publishDate.split("-").reverse().join("-"),
              );
              const dateB = new Date(
                b.publishDate.split("-").reverse().join("-"),
              );

              if (direction === "newest") {
                return dateB - dateA; // High to Low (Dec 2024 -> Jan 2024)
              }
              return dateA - dateB; // Low to High (Jan 2024 -> Dec 2024)
            });

          let resultArr = [];

          // Apply the sorting based on the parameter
          if (param.sort === "Latest" || param.sort === "Newest to Oldest") {
            resultArr = sortResults(results, "newest");
          } else if (param.sort === "Oldest to Newest") {
            resultArr = sortResults(results, "oldest");
          } else {
            // Default fallback
            resultArr = results;
          }
          // Use grouped card rendering for Scheme Summary Documents
          let pdfListHTML;
          if (dataMapMoObj.selval === "Scheme Summary Documents") {
            pdfListHTML = dataMapMoObj.renderSchemeSummaryCards(resultArr);
          } else {
            pdfListHTML = resultArr
              .map((resp) => {
                // Format data before injection
                let title = dataMapMoObj.formattitle(resp.title);
                const formattedDate =
                  resp.publishDate !== ""
                    ? dataMapMoObj.formatDatecf(resp.publishDate)
                    : "";
                const { path } = resp;
                let icon;
                let fileType;
                if (path.includes(".xls")) {
                  icon = "../../icons/file-xlsx.svg";
                  fileType = "xlsx";
                } else {
                  icon = "../../icons/pdf-icon.svg";
                  fileType = "pdf";
                }
                const pattern = new RegExp(
                  `\\b(sid(?!dh\\b)|${smallcase.join("|")})\\b`,
                  "gi",
                );
                title = title.replace(pattern, (match) => {
                  return match.toUpperCase();
                });
                // Use a template literal to build the string
                return `
            <div class="pdf-list">
                <div class="pdf-content">
                    <h3 class="pdf-title">
                      <a class= "anchortitle">${title}</a>
                    </h3>
                    <div class="pdf-desc">
                        <span class="date-ctgry">${formattedDate}</span>
                        <span class="date-ctgry">${dataMapMoObj.dataskill[dataMapMoObj.selval]}/${dataMapMoObj.selval}</span>
                    </div>
                </div>
                <div class="pdf-icon">
                    <a class= "anchorimg" href="${path}">
                      <img class="pdf-img" src="${icon}" alt="${title} ${fileType}">
                    </a>
                </div>
            </div>`;
              })
              .join("");
          }

          // 4. Update the DOM exactly once
          pdfContainer.innerHTML = pdfListHTML;
          block.querySelector(".pdf-container").classList.add("active");

          // if (typeof dataMapMoObj.syncCategoryRadioGroups === "function") {
          //   dataMapMoObj.syncCategoryRadioGroups();

          //   // 1. Find the accordion panel that is actually open/visible right now
          //   const openAccordion = block.querySelector(".accordion-field[open]");

          //   if (openAccordion) {
          //     // 2. Query scope isolated directly inside the active section panel
          //     const activeField = openAccordion.querySelector(".ctgry-field[tabindex='0']");

          //     if (activeField) {
          //       setTimeout(() => {
          //         activeField.focus({ preventScroll: true });
          //       }, 50); // 120ms ensures full DOM painting and smooth browser layout engine sync
          //     }
          //   }
          // }

          // if (typeof dataMapMoObj.syncCategoryRadioGroups === "function") {
          //   dataMapMoObj.syncCategoryRadioGroups();

          //   // Check if the user is typing in the search box before forcing focus shifts
          //   const searchField = block.querySelector("#search-field");
          //   const isUserSearching = searchField === document.activeElement;

          //   if (!isUserSearching) {
          //     // 1. Find the accordion panel that is actually open/visible right now
          //     const openAccordion = block.querySelector(".accordion-field[open]");

          //     if (openAccordion) {
          //       // 2. Query scope isolated directly inside the active section panel
          //       const activeField = openAccordion.querySelector(".ctgry-field[tabindex='0']");

          //       if (activeField) {
          //         setTimeout(() => {
          //           // Check one last time right before focus execution
          //           if (document.activeElement !== searchField) {
          //             activeField.focus({ preventScroll: true });
          //           }
          //         }, 50);
          //       }
          //     }
          //   }
          // }
          if (typeof dataMapMoObj.syncCategoryRadioGroups === "function") {
            dataMapMoObj.syncCategoryRadioGroups();

            // --- FIXED: SENIOR ENGINEER BOUNDARY PROTECTION CONTROL ---
            const searchField = block.querySelector("#search-field");
            const desktopSearchField = block.querySelector(".search-inp"); // Targeting the modern screen container input node too

            const isUserActivelySearching =
              document.activeElement === searchField ||
              document.activeElement === desktopSearchField;

            // If the user's cursor is actively engaged inside a search text box context, DO NOT hijack focus layout positions!
            if (!isUserActivelySearching) {
              const openAccordion = block.querySelector(
                ".accordion-field[open]",
              );
              if (openAccordion) {
                const activeField = openAccordion.querySelector(
                  ".ctgry-field[tabindex='0']",
                );
                if (activeField) {
                  setTimeout(() => {
                    if (
                      document.activeElement !== searchField &&
                      document.activeElement !== desktopSearchField
                    ) {
                      activeField.focus({ preventScroll: true });
                    }
                  }, 50);
                }
              }
            }
          }

          const items = Array.from(
            block.querySelectorAll(".pdf-container .pdf-list"),
          );
          const itemsPerPage = items.slice(0, 9).length;
          if (items.length > itemsPerPage) {
            dataMapMoObj.setupPagination(block, items, itemsPerPage);
          }
          pdfContainer.addEventListener("click", (e) => {
            // Skip for Scheme Summary Documents - popup handles downloads
            if (dataMapMoObj.selval === "Scheme Summary Documents") return;
            const link = e.target.closest(".anchortitle, .anchorimg");

            if (link) {
              const url = link.getAttribute("href");

              if (url && url.toLowerCase().endsWith(".pdf")) {
                e.preventDefault();
                const fileName = url.split("/").pop();
                dataMapMoObj.handleDownload(url, fileName);
              }
            }
          });
          dataMapMoObj.handleDownload = (url, fileName) => {
            fetch(url)
              .then((response) => {
                if (!response.ok) throw new Error("Network error");
                return response.blob();
              })
              .then((blob) => {
                const blobUrl = window.URL.createObjectURL(blob);
                const alink = document.createElement("a");

                // Critical: Set these attributes for iOS compatibility
                alink.style.display = "none";
                alink.href = blobUrl;
                alink.download = fileName;
                alink.target = "_blank"; // Helpful for mobile Safari fallback

                document.body.appendChild(alink); // FIXED: was 'a', now 'alink'
                alink.click();

                // Cleanup
                setTimeout(() => {
                  window.URL.revokeObjectURL(blobUrl);
                  alink.remove();
                }, 100);
              })
              .catch((err) => {
                console.error("Download failed, falling back:", err);
                // Fallback: Open in new tab if Fetch/CORS fails
                window.open(url, "_blank");
              });
          };
          if (
            dataMapMoObj.selval === "Scheme Summary Documents" &&
            !dataMapMoObj.isProcessed
          ) {
            const getAddendums = (data) => {
              if (!Array.isArray(data)) return {};
              const monthNames = [
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
              ];
              const timeline = {};

              data.forEach((scheme) => {
                if (scheme.year && scheme.month) {
                  if (!timeline[scheme.year]) timeline[scheme.year] = new Set();
                  timeline[scheme.year].add(scheme.month.toLowerCase());
                }
              });

              const finalOutput = {};

              // Sort years descending (2024, 2023...)
              Object.keys(timeline)
                .sort((a, b) => b - a)
                .forEach((year) => {
                  // Sort months descending (Dec, Nov...)
                  finalOutput[year] = Array.from(timeline[year]).sort(
                    (a, b) => monthNames.indexOf(b) - monthNames.indexOf(a),
                  );
                });

              return finalOutput;
            };

            const addendums = getAddendums(dataMapMoObj.results);
            dataMapMoObj.dropdown["scheme-summary-document"] = addendums;

            dataMapMoObj.isProcessed = true;
            // console.log(addendums);
            dataMapMoObj.renderdrop(block);
          } else if (param.month === "" && param.year !== "") {
            // AJ27
            // dataMapMoObj.dropdown[dataMapMoObj.keyval[dataMapMoObj.selval]][param.year];
            const monthContainer = block
              .querySelector("#month-label")
              .closest(".smy-drpdwn-wrap");
            const monthMenu = monthContainer.querySelector(".drpdwn-menu");
            const monthLabel = monthContainer.querySelector(".drpdwn-sltxt");
            monthLabel.textContent = "";
            dataMapMoObj.param.month = "";
            const selval = dataMapMoObj.keyvaldrop[dataMapMoObj.selval];
            const yeardrop = dataMapMoObj.dropdown[selval];
            let monthsArr = yeardrop[dataMapMoObj.param.year];
            if (monthsArr === undefined) {
              monthsArr = [];
            }
            const monthOrder = [
              "jan",
              "feb",
              "mar",
              "apr",
              "may",
              "jun",
              "jul",
              "aug",
              "sep",
              "oct",
              "nov",
              "dec",
            ];

            monthsArr.sort(
              (a, b) => monthOrder.indexOf(a) - monthOrder.indexOf(b),
            );
            const initialMonthShort = monthsArr[0];
            const initialMonthFull =
              dataMapMoObj.monthLookup[initialMonthShort];

            monthMenu.innerHTML = monthsArr
              .map(
                (m) =>
                  `<button class="smy-drpdwn-list drpdwn-list" type="button" data-short="${m}">${dataMapMoObj.monthLookup[m]}</button>`,
              )
              .join("");
            // monthLabel.textContent = initialMonthFull;

            // --- MOBILE LOGIC: MONTHS ---
            const mobileMonthBody = block.querySelector(
              ".period-filter .accordion-field:nth-child(1) .accordion-body",
            );
            if (mobileMonthBody) {
              mobileMonthBody.innerHTML = "";
              mobileMonthBody.innerHTML = monthsArr
                .map(
                  (m) => `
              <div class="period-field cmmn-field">
                <input class="period-inp cmmn-inp" type="radio" id="m-month-${m}" name="mobile-month" ${m === initialMonthShort ? "checked" : ""}>
                <label class="period-label cmmn-label" for="m-month-${m}">${dataMapMoObj.monthLookup[m]}</label>
              </div>
            `,
                )
                .join("");
            }
          }
          dataMapMoObj.syncMobileView(block, dataMapMoObj.param.month);
          dataMapMoObj.syncMobileView(block, dataMapMoObj.param.year);
          dataMapMoObj.param.month = "";
          dataMapMoObj.toggleLoaderSpinner(
            block.querySelector(".filtered-content"),
            false,
          );
        } else if (
          dataMapMoObj.selval ===
          "Risk Adjusted Returns - Information Ratio (IR)"
        ) {
          block
            .querySelector(".filtered-content .no-docs-container")
            .classList.remove("active");
          dataMapMoObj.toggleLoaderSpinner(
            block.querySelector(".filtered-content"),
            false,
          );
        } else {
          block.querySelector(".no-docs-container").classList.add("active");
          dataMapMoObj.toggleLoaderSpinner(
            block.querySelector(".filtered-content"),
            false,
          );
        }
      }
    })
    .catch((error) => {
      console.error(error);
      dataMapMoObj.toggleLoaderSpinner(
        block.querySelector(".filtered-content"),
        false,
      );
    });
};

dataMapMoObj.searchfunc = (block) => {
  let debounceTimer;
  let activeSearchRequestId = 0;
  let prevSearchLength = 0;
  let isFullTriggerScreen = false;
  let currentApiResults = [];
  const searchConfig = {
    minChars: 3,
  };

  const monthMap = {
    jan: { full: "January", index: 0 },
    feb: { full: "February", index: 1 },
    mar: { full: "March", index: 2 },
    apr: { full: "April", index: 3 },
    may: { full: "May", index: 4 },
    jun: { full: "June", index: 5 },
    jul: { full: "July", index: 6 },
    aug: { full: "August", index: 7 },
    sep: { full: "September", index: 8 },
    oct: { full: "October", index: 9 },
    nov: { full: "November", index: 10 },
    dec: { full: "December", index: 11 },
  };

  const searchInput = block.querySelector("#search-field");
  const dropdown = block.querySelector(".docs-searchlist");
  const resultsWrapper = block.querySelector(".docs-list-wrap");
  const countContainer = block.querySelector(".search-count-desc");
  const categoryOverlay = block.querySelector(".category-overlay");
  const statusText = block.querySelector("#search-field-status");
  const nonSearchableCategories = [
    "KYC & Redressal of Complaints",
    "Guidelines for Transmission of Units (AMFI Circular No. 110)",
    "Remunerations",
    "Risk Adjusted Returns - Information Ratio (IR)",
    "AMFI IAP",
    "Grievance Redressal Mechanism",
    "Disclosure of Empanelment Details of Mutual Fund Distributors",
    "Disclosure of Empanelment Details of PMS Distributors"
  ];
  const cancelBtn = ensureCancelButton(
    block.querySelector(".search-wrapper .cancel-search"),
  );
  const closeSearchDropdown = () => {
    if (dropdown?.contains(document.activeElement)) {
      searchInput?.focus();
    }
    dropdown?.classList.remove("active");
    searchInput?.setAttribute("aria-expanded", "false");
  };
  const closeAllPopups = () => {
    closeSearchDropdown();
    block.querySelectorAll(".cmmn-overlay.active").forEach((overlay) => {
      overlay.classList.remove("active");
    });
    block
      .querySelectorAll(".smy-select-drpdwn.active, .cmmn-select-drpdwn.active")
      .forEach((menu) => {
        menu.classList.remove("active");
      });
    block.closest("body")?.classList.remove("scroll-stop");
  };

  // for the search result dropdown show when click or focus on the input
  const openSearchDropdown = () => {
    if (searchInput && searchInput.value.length >= 3) {
      dropdown?.classList.add("active");
      searchInput.setAttribute("aria-expanded", "true");
    } else {
      dropdown?.classList.remove("active");
      searchInput.setAttribute("aria-expanded", "false");
    }
  };

  const showSearchLoader = () => {
    resultsWrapper.innerHTML = `
    <li class="search-loader">
      <div class="loader-spinner loader-active">
        <div class="spinner" role="img" aria-label="Loading search results">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </li>
  `;
    dropdown?.classList.add("active");
  };

  const hideSearchLoader = () => {
    resultsWrapper.querySelector(".search-loader")?.remove();
  };

  searchInput?.addEventListener("click", openSearchDropdown);
  searchInput?.addEventListener("focus", openSearchDropdown);

  /**
   * 1. UPDATE MAIN SCREEN RESULTS
   */
  const updateMainScreenResults = (results) => {
    const pdfContainer = block.querySelector(
      ".pdf-container .pdf-list-content",
    );
    const noDocs = block.querySelector(".no-docs-container");
    const pdfParent = block.querySelector(".pdf-container");
    const filteredContent = block.querySelector(".filtered-content");

    if (!pdfContainer || !filteredContent) return;

    // --- LOGIC: REMOVE ACTIVE CLASS FROM LEVEL 1 CHILDREN (Including download-tab-text) ---
    Array.from(filteredContent.children).forEach((child) => {
      child.classList.remove("active");
    });

    // FIX: Remove specific pagination elements to prevent duplication
    block
      .querySelectorAll(
        ".download-pagination-footer, .pagination, .pagination-container, .pagination-wrapper",
      )
      .forEach((el) => el.remove());

    dropdown?.classList.remove("active");
    pdfContainer.innerHTML = "";
    noDocs?.classList.remove("active");
    // pdfParent?.classList.remove('active'); // Handled by the Level 1 loop above

    if (!results || results.length === 0) {
      noDocs?.classList.add("active");
      return;
    }

    function titledata(title) {
      let titlval = dataMapMoObj.formattitle(title);
      const pattern = new RegExp(`(sid(?!dh)|${smallcase.join("|")})`, "gi");
      titlval = titlval.replace(pattern, (match) => {
        return match.toUpperCase();
      });
      return titlval;
    }

    dataMapMoObj.results = results;
    pdfContainer.innerHTML = results
      .map(
        (resp) => `
        <div class="pdf-list">
            <div class="pdf-content">
                <h3 class="pdf-title"><a class="anchortitle">${titledata(resp.title)}</a></h3>
                <div class="pdf-desc">
                    <span class="date-ctgry">${resp.publishDate !== "" ? dataMapMoObj.formatDatecf(resp.publishDate) : ""}</span>
                    <span class="date-ctgry">${dataMapMoObj.findMapping(resp.category)}/${dataMapMoObj.formattitle(resp.category) || ""}</span>
                </div>
            </div>
            <div class="pdf-icon"><a class="anchorimg" href="${resp.path.includes(".xls") ? "../../icons/file-xlsx.svg" : "../../icons/pdf-icon.svg"}"><img class="pdf-img" src="../../icons/pdf-icon.svg" alt="${dataMapMoObj.formattitle(resp.title)} ${resp.path.includes(".xls") ? "xlsx" : "pdf"}"></a></div>
        </div>`,
      )
      .join("");

    pdfParent?.classList.add("active");

    // Update Result Description Text within the active parent
    const strongTerm = searchInput.value.trim();
    const resultDescWrap = pdfParent.querySelector(".full-result-desc");
    if (resultDescWrap) {
      resultDescWrap.innerHTML = `<p class="result-desc">Found ${currentApiResults.length} results for <strong class="result-strong">“${strongTerm}”</strong>. There are ${results.length} documents under selected categories.</p>`;
    }

    const items = Array.from(
      block.querySelectorAll(".pdf-container .pdf-list"),
    );
    if (items.length > 9) dataMapMoObj.setupPagination(block, items, 9);
  };

  /**
   * 2. COMBINED FILTER LOGIC (Month/Year/Category)
   */
  const applyAllFilters = () => {
    let filtered = [...currentApiResults];

    // Query active selected interactive items in the modern state
    const selectedFields = Array.from(
      block.querySelectorAll('.ctgry-field[aria-checked="true"]'),
    );

    const checkCountSpan = block.querySelector(".check-count");
    if (checkCountSpan) {
      checkCountSpan.textContent = ` (${selectedFields.length} selected)`;
    }

    if (selectedFields.length > 0) {
      const selectedValues = selectedFields.map((field) => {
        const textLabel = field.textContent.trim();
        return dataMapMoObj.keyval[textLabel] || "";
      });
      filtered = filtered.filter((item) =>
        selectedValues.includes(item.category),
      );
    }

    updateMainScreenResults(filtered);
  };

  /**
   * 3. TOGGLE FILTER TYPE & DYNAMIC DATE RENDERING
   */
  const toggleFilterType = (isSearchActive, results) => {
    const ctgryGroups = block.querySelectorAll(".ctgry-group");
    const query = searchInput.value.trim();
    const isTrulyActive =
      isSearchActive && query.length >= searchConfig.minChars;

    isTrulyActive
      ? block
        .querySelector(".pdf-container")
        ?.classList.add("fullresult-active")
      : block
        .querySelector(".pdf-container")
        ?.classList.remove("fullresult-active");

    const uniqueCategories = isTrulyActive
      ? [...new Set(results.map((i) => i.category))]
      : [];

    if (isTrulyActive) {
      block.querySelectorAll(".cmmn-select-drpdwn").forEach((drp) => {
        drp.onclick = (e) => {
          if (e.target.classList.contains("drpdwn-list")) {
            const displayBtn = drp.querySelector(".drpdwn-sltxt");
            displayBtn.textContent = e.target.textContent;
            drp.classList.remove("active");
            drp.closest(".cmmn-drpdwn-wrap").classList.remove("active");
            if (isTrulyActive) applyAllFilters();
          }
        };
      });
    }

    ctgryGroups.forEach((group) => {
      const currentFields = Array.from(group.querySelectorAll(".ctgry-field"));

      if (!isTrulyActive) {
        // --- LINK NAVIGATION SINGLE-SELECT MODE ---
        group.removeAttribute("role");

        currentFields.forEach((field) => {
          const uiLabel = field.textContent.trim();

          // FIX: Always ensure visibility parameters reset cleanly based on uiLabel, not empty map values
          field.style.display = uiLabel === "" || uiLabel === "Guidelines for Transmission of Units (AMFI Circular No. 110)" ? "none" : "flex";

          if (field.tagName === "A") {
            const isPageActive = field.getAttribute("aria-current") === "page";
            if (isPageActive) {
              field.classList.add("active-link");
            } else {
              field.classList.remove("active-link");
            }
            return;
          }

          const targetKey = Object.keys(dataMapMoObj.keyvalurl).find(
            (key) => dataMapMoObj.keyvalurl[key] === uiLabel,
          );
          const isChecked =
            targetKey === window.location.href.split("/").at(-1);
          const computedHref = `${window.location.origin}/downloads/${targetKey || ""}`;

          const newField = document.createElement("a");
          newField.className = `ctgry-field ${isChecked ? "active-link" : ""}`;
          newField.href = computedHref;
          newField.setAttribute("aria-current", isChecked ? "page" : "false");
          newField.style.cssText = `display: ${uiLabel === "" || uiLabel === "Guidelines for Transmission of Units (AMFI Circular No. 110)" ? "none" : "flex"}; text-decoration: none; color: inherit;`;
          newField.textContent = uiLabel;

          newField.onclick = (e) => {
            if (window.innerWidth < 786) {
              e.preventDefault();
              group
                .querySelectorAll(".category-overlay .ctgry-field")
                .forEach((sibling) => {
                  sibling.removeAttribute("aria-current");
                  sibling.classList.remove("active-link");
                });
              newField.setAttribute("aria-current", "page");
              newField.classList.add("active-link");
              dataMapMoObj.selval = uiLabel;
              dataMapMoObj.param.category = dataMapMoObj.keyval[uiLabel];
              if (targetKey) {
                dataMapMoObj.keyvalurl[targetKey] = uiLabel;
              }
            }
          };
          field.replaceWith(newField);
        });
      } else {
        // --- ACTIVE MULTI-SELECT SEARCH MODE ---
        group.setAttribute("role", "group");

        currentFields.forEach((field) => {
          const uiLabel = field.textContent.trim();
          const mappedValue = dataMapMoObj.keyval[uiLabel] || "";
          const isAvailable = uniqueCategories.includes(mappedValue);

          if (field.tagName === "BUTTON") {
            field.style.display = isAvailable && uiLabel !== "Guidelines for Transmission of Units (AMFI Circular No. 110)" ? "flex" : "none";
            return;
          }

          const newField = document.createElement("button");
          newField.type = "button";
          newField.className = "ctgry-field multiselect-checkbox";
          newField.setAttribute("role", "checkbox");
          newField.setAttribute("aria-checked", "false");
          newField.style.cssText = `display: ${isAvailable ? "flex" : "none"}; background: none; border: none; padding: 2.5px; text-align: left; width: 100%; font-family: inherit; cursor: pointer;`;
          newField.textContent = uiLabel;

          newField.onclick = (e) => {
            e.preventDefault();
            const isCurrentlyChecked =
              newField.getAttribute("aria-checked") === "true";

            if (isCurrentlyChecked) {
              newField.setAttribute("aria-checked", "false");
              newField.classList.remove("active-link");
            } else {
              newField.setAttribute("aria-checked", "true");
              newField.classList.add("active-link");
            }

            applyAllFilters();
            if (typeof syncCategoryRadioGroups === "function") {
              syncCategoryRadioGroups();
            }
          };
          field.replaceWith(newField);
        });
      }
    });

    // Reset accordion wrapper layouts and collapse states cleanly back to initialization rules
    block.querySelectorAll(".accordion-field").forEach((accordion, idx) => {
      if (accordion.closest(".category-overlay")) {
        if (isTrulyActive) {
          const hasVisible = Array.from(
            accordion.querySelectorAll(".ctgry-field"),
          ).some((f) => f.style.display === "flex");
          accordion.style.display = hasVisible ? "block" : "none";
          if (hasVisible) {
            accordion.setAttribute("open", "");
          } else {
            accordion.removeAttribute("open");
          }
        } else {
          accordion.style.display = "block";
          const hasActiveChild = Array.from(
            accordion.querySelectorAll(".ctgry-field"),
          ).some(
            (field) =>
              field.classList.contains("active-link") ||
              field.getAttribute("aria-current") === "page",
          );
          const isCurrentlySelectedGroup =
            dataMapMoObj.selval &&
            accordion.querySelector(".ctgry-field")?.textContent.trim() ===
            dataMapMoObj.selval;

          // Retain state explicitly rather than toggling open attributes up and down continuously
          if (hasActiveChild || isCurrentlySelectedGroup) {
            if (!accordion.hasAttribute("open"))
              accordion.setAttribute("open", "");
          } else if (!dataMapMoObj.selval && idx === 0) {
            if (!accordion.hasAttribute("open"))
              accordion.setAttribute("open", "");
          } else {
            accordion.removeAttribute("open");
          }
        }
      }
    });

    if (typeof syncCategoryRadioGroups === "function") {
      syncCategoryRadioGroups();
    }
  };

  /**
   * 4. BATCH SELECTION (SELECT ALL / CLEAR ALL)
   */
  block.querySelectorAll(".accordion-field").forEach((accordion) => {
    accordion.addEventListener("click", (e) => {
      if (e.target.classList.contains("stcl-btn")) {
        const isSelectAll =
          e.target.textContent.trim().toLowerCase() === "select all";
        const visibleFields = Array.from(
          accordion.querySelectorAll('.ctgry-field[style*="display: flex"]'),
        );

        visibleFields.forEach((field) => {
          if (field.tagName === "BUTTON") {
            field.setAttribute("aria-checked", isSelectAll ? "true" : "false");
            if (isSelectAll) {
              field.classList.add("active-link");
            } else {
              field.classList.remove("active-link");
            }
          }
        });

        applyAllFilters();
        if (typeof syncCategoryRadioGroups === "function") {
          syncCategoryRadioGroups();
        }
      }
    });
  });

  /**
   * 5. MOBILE APPLY LOGIC
   */
  const mobileApplyBtn = block.querySelector(".category-overlay .applybtn");
  if (mobileApplyBtn) {
    mobileApplyBtn.onclick = () => {
      const arr = [
        "KYC & Redressal of Complaints",
        "Guidelines for Transmission of Units (AMFI Circular No. 110)",
        "Remunerations",
        "Risk Adjusted Returns - Information Ratio (IR)",
        "AMFI IAP",
        "Grievance Redressal Mechanism",
        "Disclosure of Empanelment Details of Mutual Fund Distributors",
        "Disclosure of Empanelment Details of PMS Distributors"
      ];
      if (!arr.includes(dataMapMoObj.selval)) {
        applyAllFilters();
      }
      // Optional: block.querySelector('.ctgrys-filter')?.classList.remove('active');
    };
  }

  /**
   * 6. SEARCH EXECUTION
   */
  const triggerFullView = () => {
    if (currentApiResults.length > 0) {
      isFullTriggerScreen = true;

      // Clear checking flags across buttons dynamically on new view trigger
      block.querySelectorAll(".ctgry-field").forEach((field) => {
        field.setAttribute("aria-checked", "false");
        field.classList.remove("active-link");
      });

      const checkCountSpan = block.querySelector(".check-count");
      if (checkCountSpan) checkCountSpan.textContent = " (0 selected)";

      toggleFilterType(true, currentApiResults);
      updateMainScreenResults(currentApiResults);
      block.querySelector(".download-container").classList.add("search-active");
      block.querySelector(".result-desc .result-strong").textContent =
        `“${searchInput.value.trim()}”`;
    }
  };


  const highlightMatch = (text, query) => {
    if (!query || !text) return text;
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return text.replace(
      new RegExp(`(${escapedQuery})`, "gi"),
      '<strong class="search-highlight">$1</strong>',
    );
  };

  const renderResults = (results, query) => {
    resultsWrapper.innerHTML = "";

    // sort function for the donwload search on title
    // 1. Filter out items that do NOT contain the search query at all
    // 1. FILTER the results first using the regex cleanup
    const filteredResults = results.filter((item) => {
      const cleanTitle = (item.title || "")
        .trim()
        .toLowerCase()
        .replace(/\s*-\s*|_/g, " ");
      const searchStr = query.toLowerCase().trim();

      // This ensures items containing the search string are kept, even if they have _ or - in the API
      return cleanTitle.includes(searchStr);
    });

    // 2. SORT the filtered results (Your existing logic) // AJ27
    const parsePublishDate = (dateValue) => {
      const raw = String(dateValue || "").trim();
      if (!raw) return 0;

      // Handles your backend format: "10-02-2026" (DD-MM-YYYY)
      const parts = raw.split(/[-/\s]+/);
      if (parts.length === 3 && parts[0].length <= 2 && parts[2].length === 4) {
        const day = parseInt(parts[0], 10);
        const year = parseInt(parts[2], 10);
        const monthStr = parts[1].toLowerCase();

        let month;
        if (isNaN(monthStr)) {
          const monthMap = {
            jan: 0,
            feb: 1,
            mar: 2,
            apr: 3,
            may: 4,
            jun: 5,
            jul: 6,
            aug: 7,
            sep: 8,
            oct: 9,
            nov: 10,
            dec: 11,
          };
          month = monthMap[monthStr.slice(0, 3)];
        } else {
          month = parseInt(monthStr, 10) - 1; // Converts "02" to 1 (February)
        }

        if (
          !Number.isNaN(day) &&
          !Number.isNaN(year) &&
          month !== undefined &&
          !Number.isNaN(month)
        ) {
          return new Date(year, month, day).getTime();
        }
      }

      const direct = Date.parse(raw);
      if (!Number.isNaN(direct)) return direct;

      return 0;
    };

    const sortedResults = [...filteredResults].sort((a, b) => {
      const aTitle = (a.title || "")
        .trim()
        .toLowerCase()
        .replace(/\s*-\s*|_/g, " ");
      const bTitle = (b.title || "")
        .trim()
        .toLowerCase()
        .replace(/\s*-\s*|_/g, " ");
      const searchStr = query.toLowerCase().trim();

      // Latest publish date gets highest priority // AJ27
      const aDate = parsePublishDate(a.publishDate);
      const bDate = parsePublishDate(b.publishDate);
      if (aDate !== bDate) return bDate - aDate;

      // Exact match gets second priority
      if (aTitle === searchStr && bTitle !== searchStr) return -1;
      if (bTitle === searchStr && aTitle !== searchStr) return 1;

      // Starts with the search query gets third priority // AJ27
      const aStarts = aTitle.startsWith(searchStr);
      const bStarts = bTitle.startsWith(searchStr);
      if (aStarts && !bStarts) return -1;
      if (bStarts && !aStarts) return 1;

      // Default to alphabetical sorting
      return aTitle.localeCompare(bTitle);
    });

    // 3. Clear previous UI results before rendering the new ones
    resultsWrapper.innerHTML = "";

    // 4. Render the clean, filtered, and sorted list
    sortedResults.forEach((item) => {
      let itemtitle = dataMapMoObj.formattitle(item.title);
      const pattern = new RegExp(`(sid(?!dh)|${smallcase.join("|")})`, "gi");

      itemtitle = itemtitle.replace(
        pattern,
        (match) => `${match.toUpperCase()}`,
      );
      const highlightedTitle = highlightMatch(itemtitle, query);
      const resultItem = document.createElement("li");
      resultItem.className = "docs-list";

      resultItem.innerHTML = `
        <div class="docs-content">
           <a href="${item.path}" class="docs-title docs-name" target="_Blank" rel="noopener noreferrer">
           ${highlightedTitle}
           </a>
          <div class="docs-desc">
            <span class="search-date-ctgry">
              ${item.publishDate !== "" ? dataMapMoObj.formatDatecf(item.publishDate) : ""}
            </span>
            <span class="search-date-ctgry">
              ${dataMapMoObj.findMapping(item.category)}/${dataMapMoObj.formattitle(item.category) || ""}
            </span>
          </div>
        </div>
      `;
      resultsWrapper.appendChild(resultItem);
    });

    const totalCount = sortedResults ? sortedResults.length : 0;
    if (countContainer) {
      countContainer.innerHTML =
        totalCount > 0
          ? `<p class="count-desc" style="cursor:pointer">Hit enter to view all ${totalCount} results for “${query}”</p>`
          : "";
      countContainer.style.display = totalCount > 0 ? "block" : "none";
    }
    if (statusText) {
      statusText.textContent =
        totalCount > 0
          ? `${totalCount} suggestions available.`
          : "No suggestions available.";
    }
    if (totalCount === 0) {
      resultsWrapper.innerHTML = '<li class="no-content">No results found</li>';
      return;
    }
    dropdown?.classList.add("active");
  };

  const executeSearch = (query) => {
    const term = query?.trim() || "";
    if (term.length < searchConfig.minChars) {
      activeSearchRequestId += 1;
      hideSearchLoader();
      dropdown?.classList.remove("active");
      currentApiResults = [];
      toggleFilterType(false);
      if (statusText) statusText.textContent = "";
      return;
    }

    if (nonSearchableCategories.includes(dataMapMoObj.selval)) {
      activeSearchRequestId += 1;
      hideSearchLoader();
      currentApiResults = [];
      resultsWrapper.innerHTML =
        '<li class="no-content">No results found</li>';
      if (countContainer) {
        countContainer.innerHTML = "";
        countContainer.style.display = "none";
      }
      if (statusText) {
        statusText.textContent = "No results found";
      }
      dropdown?.classList.add("active");
      return;
    }

    const requestId = activeSearchRequestId + 1;
    activeSearchRequestId = requestId;
    showSearchLoader();

    const selectedCategory = dataMapMoObj.keyval[dataMapMoObj.selval] || "";
    searchDownloadResults({
      searchQuery: term,
      type: dataMapMoObj.param.type || "",
      category: selectedCategory,
    })
      .then((data) => {
        if (requestId !== activeSearchRequestId) return;
        currentApiResults = data.results || [];
        if (countContainer?.querySelector(".count-desc")) {
          countContainer.querySelector(".count-desc").textContent = "";
        }
        // dataMapMoObj.toggleLoaderSpinner(block.querySelector('.filtered-content'), false);
        renderResults(currentApiResults, term);
        // toggleFilterType(false, currentApiResults);
        // applyAllFilters();
        openSearchDropdown();
      })
      .catch((err) => {
        if (requestId !== activeSearchRequestId) return;
        resultsWrapper.innerHTML =
          '<li class="no-content">No results found</li>';
        if (dropdown.querySelector(".count-desc")) {
          dropdown.querySelector(".count-desc").textContent = "";
        }
        countContainer.style.display = "none";
      })
      .finally(() => {
        if (requestId === activeSearchRequestId) {
          hideSearchLoader();
        }
      });
  };

  // --- 7. LISTENERS ---
  countContainer?.addEventListener("click", triggerFullView);

  searchInput.addEventListener("input", (e) => {
    const val = e.target.value;
    // Sanitize input - remove special characters, emojis, and HTML tags
    const cleaned = val.replace(/[^A-Za-z0-9 _-]/g, "");
    const cleanVal = cleaned;

    // Update input value to only contain allowed characters
    if (val !== cleanVal) {
      e.target.value = cleanVal;
    }

    const crossedBelowMinOnFullScreen =
      isFullTriggerScreen &&
      prevSearchLength <= searchConfig.minChars &&
      cleanVal.length < searchConfig.minChars;

    if (cleanVal.length < searchConfig.minChars) {
      dropdown?.classList.remove("active");
      toggleFilterType(false);
      if (cancelBtn) {
        cancelBtn.style.display = cleanVal.length > 0 ? "flex" : "none";
      }

      const checkCountSpan = block.querySelector(".check-count");
      if (checkCountSpan) checkCountSpan.textContent = " (0 selected)";

      if (cleanVal.length === 0) {
        dataMapMoObj.selecaterogy(dataMapMoObj.selval, {
          shouldScroll: false,
        });
        dataMapMoObj.dropEvent = "";
        block
          .querySelector(".download-container")
          .classList.remove("search-active");
        const complianceTabs = [
          "KYC & Redressal of Complaints",
          "Guidelines for Transmission of Units (AMFI Circular No. 110)",
          "Remunerations",
          "Grievance Redressal Mechanism",
          "AMFI IAP",
          "Disclosure of Empanelment Details of Mutual Fund Distributors",
          "Disclosure of Empanelment Details of PMS Distributors"
        ];
        if (
          dataMapMoObj.selval ===
          "Risk Adjusted Returns - Information Ratio (IR)"
        ) {
          block
            .querySelector(".upper-filter")
            ?.classList.add("risk-return-active");
          block
            .querySelector(".filter-content .sticky-fields")
            ?.classList.add("risk-return-active");
          block.querySelector(".pdf-container")?.classList.remove("active");
        } else if (complianceTabs.includes(dataMapMoObj.selval)) {
          block.querySelector(".pdf-container")?.classList.remove("active");
          block
            .querySelector(".download-container")
            ?.classList.add("tab-text-active");
          if (
            dataMapMoObj.selval === "AMFI IAP" ||
            dataMapMoObj.selval === "Grievance Redressal Mechanism"
          ) {
            block.querySelector(".tab-pdf-card").classList.add("active");
            if (block.querySelector(".download-pagination-footer")) {
              block.querySelector(".download-pagination-footer").remove();
            }
          }
        } else {
          // block.querySelector(".pdf-list-content").innerHTML = "";
          dataMapMoObj.param.category =
            dataMapMoObj.keyval[dataMapMoObj.selval];
        }
        if (crossedBelowMinOnFullScreen) {
          dataMapMoObj.categoryfilter(block, dataMapMoObj.param, {
            suppressLoader: true,
          });
        }
      } else {
        // Returning from search mode to base UI: keep category radios interactive.
        dataMapMoObj.dropEvent = "";
        if (typeof dataMapMoObj.selecaterogy === "function") {
          dataMapMoObj.selecaterogy(dataMapMoObj.selval, {
            shouldScroll: false,
          });
        }
      }
    }
    prevSearchLength = cleanVal.length;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => executeSearch(cleanVal), 300);
    if (cancelBtn) {
      cancelBtn.style.display = cleanVal.length > 0 ? "flex" : "none";
    }
  });

  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (nonSearchableCategories.includes(dataMapMoObj.selval)) {
        closeSearchDropdown();
        return;
      }
      updateMainScreenResults(currentApiResults);
      closeSearchDropdown();
      triggerFullView();
    }
    if (e.key === "Escape") {
      closeAllPopups();
      searchInput.blur();
    }
    if (e.key === "ArrowDown") {
      const firstSuggestion = resultsWrapper?.querySelector("a.docs-name");
      if (dropdown?.classList.contains("active") && firstSuggestion) {
        e.preventDefault();
        firstSuggestion.focus();
      }
    }
  });

  // Roving keyboard navigation across the rendered suggestion links (2.1.1)
  resultsWrapper?.addEventListener("keydown", (e) => {
    if (!["ArrowDown", "ArrowUp"].includes(e.key)) return;

    const suggestionLinks = Array.from(
      resultsWrapper.querySelectorAll("a.docs-name"),
    );
    if (!suggestionLinks.length) return;

    const currentIndex = suggestionLinks.indexOf(document.activeElement);
    e.preventDefault();

    if (e.key === "ArrowDown") {
      const next = suggestionLinks[currentIndex + 1];
      (next || suggestionLinks[0]).focus();
    }

    if (e.key === "ArrowUp") {
      if (currentIndex <= 0) {
        searchInput.focus();
      } else {
        suggestionLinks[currentIndex - 1].focus();
      }
    }
  });

  dropdown?.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeSearchDropdown();
      searchInput.focus();
    }
  });

  block.addEventListener("focusin", (e) => {
    if (!dropdown?.classList.contains("active")) return;
    const { target } = e;
    if (!dropdown.contains(target) && target !== searchInput) {
      closeSearchDropdown();
    }
  });

  block.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    closeAllPopups();
  });

  if (cancelBtn) {
    cancelBtn.style.display = searchInput.value.length > 0 ? "flex" : "none";
    cancelBtn.addEventListener("click", () => {
      searchInput.value = "";
      if (statusText) statusText.textContent = "";
      closeSearchDropdown();
      cancelBtn.style.display = "none";
      toggleFilterType(false);
      const pathLink = window.location.href.split("/").at(-1);
      const initialChecked = dataMapMoObj.keyvalurl[pathLink];
      if (initialChecked) {
        dataMapMoObj.param.category = dataMapMoObj.keyval[initialChecked];
        dataMapMoObj.categoryfilter(block, dataMapMoObj.param);
      }
    });
  }

  document.addEventListener(
    "keydown",
    (e) => {
      if (e.key !== "Escape") return;
      if (
        !dropdown?.classList.contains("active") &&
        !block.querySelector(".cmmn-overlay.active") &&
        !block.querySelector(".smy-select-drpdwn.active") &&
        !block.querySelector(".cmmn-select-drpdwn.active")
      )
        return;
      closeAllPopups();
    },
    true,
  );
};

document.addEventListener("click", (e) => {
  const docsSearchLists = document.querySelectorAll(".docs-searchlist.active");
  docsSearchLists.forEach((docsSearchList) => {
    const searchWrapper = docsSearchList.closest(".search-wrapper");
    const scopedSearchInput = searchWrapper?.querySelector("#search-field");
    const clickedInsideSearchInput =
      scopedSearchInput &&
      (e.target === scopedSearchInput || scopedSearchInput.contains(e.target));

    if (!docsSearchList.contains(e.target) && !clickedInsideSearchInput) {
      docsSearchList.classList.remove("active");
    }
  });
});
