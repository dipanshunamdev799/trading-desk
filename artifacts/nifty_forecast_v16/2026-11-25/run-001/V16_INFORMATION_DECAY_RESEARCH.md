# V16 Information decay across sessions

The primary decay grid fixes the 08:55 forecast clock across the same-morning gap, first hour, remaining cash session, same-day close, next-session return, and original three-, five-, ten- and 21-session endpoints. It compares the current eligible equal-market factor, versions delayed by 1, 2 or 5 NSE sessions, a 17-session block displacement, a three-session smooth, and the domestic-only reference. The 09:25 and 10:20 follow-up conditions the parent on the actual observed prefix. The 17:00 target keeps next opening and next close distinct. Forecast times remain tied to each comparison; a lag comparison is evaluated on identical cases. International regions receive distinct completed-session and stale-control contrasts.

## Fixed-clock information across horizons

| target | model | n | brier | crps | balanced accuracy | covered |
| --- | --- | --- | --- | --- | --- | --- |
| firsthour | domestic | 257 | 0.263165 | 0.002164 | 0.512970 | 0.723735 |
| firsthour | eq_fresh | 257 | 0.263098 | 0.002167 | 0.528121 | 0.723735 |
| firsthour | eq_lag1 | 257 | 0.263457 | 0.002163 | 0.516545 | 0.715953 |
| firsthour | eq_lag17 | 257 | 0.263548 | 0.002156 | 0.543485 | 0.731518 |
| firsthour | eq_lag2 | 257 | 0.264135 | 0.002167 | 0.508970 | 0.727626 |
| firsthour | eq_lag5 | 257 | 0.264844 | 0.002172 | 0.524333 | 0.723735 |
| firsthour | eq_smooth | 257 | 0.264192 | 0.002168 | 0.524333 | 0.731518 |
| firsthour | gift_conditional | 248 | 0.259900 | 0.002179 | 0.529729 | 0.737903 |
| five | domestic | 265 | 0.244661 | 0.010992 | 0.589282 | 0.750943 |
| five | eq_fresh | 265 | 0.245016 | 0.010999 | 0.580042 | 0.750943 |
| five | eq_lag1 | 265 | 0.244477 | 0.010991 | 0.582525 | 0.750943 |
| five | eq_lag17 | 265 | 0.246225 | 0.011017 | 0.578251 | 0.750943 |
| five | eq_lag2 | 265 | 0.243085 | 0.010975 | 0.590177 | 0.747170 |
| five | eq_lag5 | 265 | 0.243935 | 0.010996 | 0.577356 | 0.747170 |
| five | eq_smooth | 265 | 0.244164 | 0.010994 | 0.578251 | 0.750943 |
| five | gift_conditional | 253 | 0.242828 | 0.011097 | 0.617483 | 0.735178 |
| gap | domestic | 258 | 0.257213 | 0.003238 | 0.576983 | 0.720930 |
| gap | eq_fresh | 258 | 0.239192 | 0.003053 | 0.635457 | 0.759690 |
| gap | eq_lag1 | 258 | 0.262312 | 0.003247 | 0.526743 | 0.720930 |
| gap | eq_lag17 | 258 | 0.259233 | 0.003235 | 0.584495 | 0.732558 |
| gap | eq_lag2 | 258 | 0.255834 | 0.003231 | 0.584615 | 0.728682 |
| gap | eq_lag5 | 258 | 0.257594 | 0.003241 | 0.569050 | 0.720930 |
| gap | eq_smooth | 258 | 0.260932 | 0.003236 | 0.546034 | 0.724806 |
| gap | gift_conditional | 248 | 0.152550 | 0.002305 | 0.822581 | 0.846774 |
| next_gap | domestic | 257 | 0.266535 | 0.003240 | 0.516263 | 0.739300 |
| next_gap | eq_fresh | 257 | 0.266913 | 0.003224 | 0.528165 | 0.735409 |
| next_gap | eq_lag1 | 257 | 0.265082 | 0.003227 | 0.493186 | 0.731518 |
| next_gap | eq_lag17 | 257 | 0.267591 | 0.003242 | 0.504815 | 0.739300 |
| next_gap | eq_lag2 | 257 | 0.266810 | 0.003241 | 0.512235 | 0.739300 |
| next_gap | eq_lag5 | 257 | 0.266772 | 0.003235 | 0.489612 | 0.739300 |
| next_gap | eq_smooth | 257 | 0.261507 | 0.003195 | 0.527983 | 0.727626 |
| next_gap | gift_conditional | 247 | 0.265189 | 0.003260 | 0.530094 | 0.740891 |
| next_next_close | domestic | 257 | 0.252646 | 0.004985 | 0.548304 | 0.735409 |
| next_next_close | eq_fresh | 257 | 0.253810 | 0.004992 | 0.544367 | 0.735409 |
| next_next_close | eq_lag1 | 257 | 0.250140 | 0.004960 | 0.567262 | 0.723735 |
| next_next_close | eq_lag17 | 257 | 0.253404 | 0.004996 | 0.548122 | 0.735409 |
| next_next_close | eq_lag2 | 257 | 0.252459 | 0.004988 | 0.556087 | 0.735409 |
| next_next_close | eq_lag5 | 257 | 0.253585 | 0.004982 | 0.551696 | 0.739300 |
| next_next_close | eq_smooth | 257 | 0.253276 | 0.004980 | 0.555724 | 0.727626 |
| next_next_close | gift_conditional | 247 | 0.254430 | 0.005060 | 0.558295 | 0.724696 |
| one | domestic | 258 | 0.254857 | 0.005007 | 0.522536 | 0.713178 |
| one | eq_fresh | 258 | 0.248569 | 0.004892 | 0.550060 | 0.720930 |
| one | eq_lag1 | 258 | 0.255225 | 0.005013 | 0.534255 | 0.720930 |
| one | eq_lag17 | 258 | 0.254755 | 0.004986 | 0.534195 | 0.717054 |
| one | eq_lag2 | 258 | 0.252854 | 0.004993 | 0.546034 | 0.713178 |
| one | eq_lag5 | 258 | 0.256584 | 0.005021 | 0.526563 | 0.701550 |
| one | eq_smooth | 258 | 0.254872 | 0.005000 | 0.545853 | 0.717054 |
| one | gift_conditional | 248 | 0.207457 | 0.004226 | 0.733984 | 0.770161 |
| regular | domestic | 258 | 0.249278 | 0.003693 | 0.524170 | 0.751938 |
| regular | eq_fresh | 258 | 0.249995 | 0.003702 | 0.524531 | 0.748062 |
| regular | eq_lag1 | 258 | 0.247930 | 0.003680 | 0.535714 | 0.748062 |
| regular | eq_lag17 | 258 | 0.249230 | 0.003690 | 0.543651 | 0.740310 |
| regular | eq_lag2 | 258 | 0.251030 | 0.003698 | 0.543290 | 0.748062 |
| regular | eq_lag5 | 258 | 0.250826 | 0.003701 | 0.543831 | 0.748062 |
| regular | eq_smooth | 258 | 0.249878 | 0.003695 | 0.524351 | 0.748062 |
| regular | gift_conditional | 248 | 0.246197 | 0.003651 | 0.567330 | 0.754032 |
| remaining | domestic | 257 | 0.251255 | 0.002956 | 0.552750 | 0.750973 |
| remaining | eq_fresh | 257 | 0.252707 | 0.002961 | 0.533339 | 0.758755 |
| remaining | eq_lag1 | 257 | 0.251511 | 0.002955 | 0.541122 | 0.762646 |
| remaining | eq_lag17 | 257 | 0.251655 | 0.002962 | 0.537185 | 0.758755 |
| remaining | eq_lag2 | 257 | 0.252664 | 0.002964 | 0.529403 | 0.766537 |
| remaining | eq_lag5 | 257 | 0.252825 | 0.002963 | 0.517624 | 0.762646 |
| remaining | eq_smooth | 257 | 0.251361 | 0.002961 | 0.552780 | 0.758755 |
| remaining | gift_conditional | 248 | 0.248952 | 0.002908 | 0.552419 | 0.758065 |
| ten | domestic | 249 | 0.287822 | 0.019291 | 0.503427 | 0.718876 |
| ten | eq_fresh | 249 | 0.289623 | 0.019348 | 0.487172 | 0.714859 |
| ten | eq_lag1 | 249 | 0.286846 | 0.019268 | 0.514297 | 0.718876 |
| ten | eq_lag17 | 249 | 0.287944 | 0.019292 | 0.498923 | 0.718876 |
| ten | eq_lag2 | 249 | 0.288791 | 0.019321 | 0.494418 | 0.710843 |
| ten | eq_lag5 | 249 | 0.287881 | 0.019303 | 0.498923 | 0.714859 |
| ten | eq_smooth | 249 | 0.288593 | 0.019335 | 0.518801 | 0.714859 |
| ten | gift_conditional | 241 | 0.285699 | 0.019536 | 0.506534 | 0.709544 |
| three | domestic | 256 | 0.241090 | 0.008520 | 0.542968 | 0.761719 |
| three | eq_fresh | 256 | 0.242762 | 0.008515 | 0.539870 | 0.761719 |
| three | eq_lag1 | 256 | 0.241514 | 0.008518 | 0.523615 | 0.761719 |
| three | eq_lag17 | 256 | 0.241608 | 0.008522 | 0.554469 | 0.757812 |
| three | eq_lag2 | 256 | 0.241319 | 0.008523 | 0.562872 | 0.765625 |
| three | eq_lag5 | 256 | 0.241788 | 0.008535 | 0.539318 | 0.769531 |
| three | eq_smooth | 256 | 0.242004 | 0.008538 | 0.543520 | 0.765625 |
| three | gift_conditional | 246 | 0.228590 | 0.008174 | 0.632974 | 0.792683 |
| twentyone | domestic | 217 | 0.295068 | 0.031064 | 0.495125 | 0.599078 |
| twentyone | eq_fresh | 217 | 0.294996 | 0.031064 | 0.495125 | 0.599078 |
| twentyone | eq_lag1 | 217 | 0.294809 | 0.031088 | 0.499223 | 0.599078 |
| twentyone | eq_lag17 | 217 | 0.294729 | 0.031115 | 0.491027 | 0.599078 |
| twentyone | eq_lag2 | 217 | 0.295637 | 0.031075 | 0.495125 | 0.603687 |
| twentyone | eq_lag5 | 217 | 0.295774 | 0.031078 | 0.495125 | 0.599078 |
| twentyone | eq_smooth | 217 | 0.295837 | 0.031087 | 0.499223 | 0.599078 |
| twentyone | gift_conditional | 210 | 0.297077 | 0.031861 | 0.492480 | 0.609524 |
| two | domestic | 257 | 0.253172 | 0.006972 | 0.530660 | 0.778210 |
| two | eq_fresh | 257 | 0.247718 | 0.006896 | 0.557606 | 0.770428 |
| two | eq_lag1 | 257 | 0.254270 | 0.006983 | 0.504719 | 0.774319 |
| two | eq_lag17 | 257 | 0.253480 | 0.006962 | 0.532396 | 0.770428 |
| two | eq_lag2 | 257 | 0.253816 | 0.006964 | 0.527037 | 0.774319 |
| two | eq_lag5 | 257 | 0.254124 | 0.006982 | 0.531239 | 0.785992 |
| two | eq_smooth | 257 | 0.253396 | 0.006986 | 0.539642 | 0.778210 |
| two | gift_conditional | 247 | 0.232798 | 0.006625 | 0.617062 | 0.805668 |

## Paired fresh, delayed and smoothed gains

| target | candidate | control | n | gain | early gain | later gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gap | eq_fresh | domestic | 258 | 0.018021 | 0.022101 | 0.014126 | -0.009041 | 0.045082 |
| gap | eq_lag1 | eq_fresh | 258 | -0.023120 | -0.032519 | -0.014147 | -0.048022 | 0.001782 |
| gap | eq_lag17 | eq_fresh | 258 | -0.020041 | -0.021009 | -0.019116 | -0.048915 | 0.008833 |
| gap | eq_lag2 | eq_fresh | 258 | -0.016642 | -0.017841 | -0.015497 | -0.044781 | 0.011498 |
| gap | eq_lag5 | eq_fresh | 258 | -0.018402 | -0.020537 | -0.016363 | -0.045073 | 0.008269 |
| gap | eq_smooth | eq_fresh | 258 | -0.021740 | -0.028581 | -0.015209 | -0.042018 | -0.001461 |
| gap | gift_conditional | domestic | 248 | 0.106226 | 0.127976 | 0.085504 | 0.058556 | 0.153897 |
| regular | eq_fresh | domestic | 258 | -0.000717 | 0.000040 | -0.001440 | -0.002835 | 0.001402 |
| regular | eq_lag1 | eq_fresh | 258 | 0.002065 | 0.000521 | 0.003539 | -0.002807 | 0.006938 |
| regular | eq_lag17 | eq_fresh | 258 | 0.000765 | 0.000169 | 0.001334 | -0.002391 | 0.003921 |
| regular | eq_lag2 | eq_fresh | 258 | -0.001035 | -0.003279 | 0.001107 | -0.004786 | 0.002716 |
| regular | eq_lag5 | eq_fresh | 258 | -0.000831 | -0.001787 | 0.000082 | -0.004198 | 0.002537 |
| regular | eq_smooth | eq_fresh | 258 | 0.000117 | -0.000036 | 0.000263 | -0.002300 | 0.002534 |
| regular | gift_conditional | domestic | 248 | -0.000261 | -0.001504 | 0.000923 | -0.004854 | 0.004332 |
| firsthour | eq_fresh | domestic | 257 | 0.000067 | -0.000262 | 0.000384 | -0.002750 | 0.002885 |
| firsthour | eq_lag1 | eq_fresh | 257 | -0.000360 | 0.000536 | -0.001222 | -0.004140 | 0.003420 |
| firsthour | eq_lag17 | eq_fresh | 257 | -0.000450 | -0.001193 | 0.000264 | -0.009623 | 0.008723 |
| firsthour | eq_lag2 | eq_fresh | 257 | -0.001037 | -0.000775 | -0.001289 | -0.005068 | 0.002994 |
| firsthour | eq_lag5 | eq_fresh | 257 | -0.001746 | -0.003119 | -0.000426 | -0.006378 | 0.002885 |
| firsthour | eq_smooth | eq_fresh | 257 | -0.001095 | -0.000086 | -0.002064 | -0.005125 | 0.002936 |
| firsthour | gift_conditional | domestic | 248 | 0.003230 | 0.002867 | 0.003577 | -0.000957 | 0.007417 |
| remaining | eq_fresh | domestic | 257 | -0.001452 | -0.001484 | -0.001421 | -0.003412 | 0.000508 |
| remaining | eq_lag1 | eq_fresh | 257 | 0.001196 | 0.001759 | 0.000654 | -0.002789 | 0.005181 |
| remaining | eq_lag17 | eq_fresh | 257 | 0.001052 | 0.000513 | 0.001570 | -0.001227 | 0.003331 |
| remaining | eq_lag2 | eq_fresh | 257 | 0.000044 | -0.000124 | 0.000204 | -0.004061 | 0.004148 |
| remaining | eq_lag5 | eq_fresh | 257 | -0.000118 | -0.000675 | 0.000418 | -0.004823 | 0.004588 |
| remaining | eq_smooth | eq_fresh | 257 | 0.001346 | 0.002201 | 0.000524 | -0.001555 | 0.004248 |
| remaining | gift_conditional | domestic | 248 | 0.002568 | 0.002761 | 0.002384 | -0.001046 | 0.006182 |
| one | eq_fresh | domestic | 258 | 0.006289 | 0.010618 | 0.002156 | -0.005271 | 0.017848 |
| one | eq_lag1 | eq_fresh | 258 | -0.006657 | -0.011483 | -0.002050 | -0.017842 | 0.004529 |
| one | eq_lag17 | eq_fresh | 258 | -0.006186 | -0.011492 | -0.001122 | -0.017989 | 0.005617 |
| one | eq_lag2 | eq_fresh | 258 | -0.004285 | -0.008294 | -0.000458 | -0.016545 | 0.007975 |
| one | eq_lag5 | eq_fresh | 258 | -0.008015 | -0.011685 | -0.004512 | -0.020046 | 0.004016 |
| one | eq_smooth | eq_fresh | 258 | -0.006303 | -0.009689 | -0.003071 | -0.015587 | 0.002981 |
| one | gift_conditional | domestic | 248 | 0.046589 | 0.063085 | 0.030872 | 0.020369 | 0.072809 |
| next_gap | eq_fresh | domestic | 257 | -0.000378 | -0.006485 | 0.005495 | -0.008040 | 0.007283 |
| next_gap | eq_lag1 | eq_fresh | 257 | 0.001830 | 0.013214 | -0.009118 | -0.009931 | 0.013592 |
| next_gap | eq_lag17 | eq_fresh | 257 | -0.000679 | 0.006463 | -0.007547 | -0.009565 | 0.008208 |
| next_gap | eq_lag2 | eq_fresh | 257 | 0.000103 | 0.007320 | -0.006839 | -0.009578 | 0.009783 |
| next_gap | eq_lag5 | eq_fresh | 257 | 0.000141 | 0.004539 | -0.004090 | -0.010886 | 0.011167 |
| next_gap | eq_smooth | eq_fresh | 257 | 0.005406 | 0.014391 | -0.003236 | -0.005308 | 0.016120 |
| next_gap | gift_conditional | domestic | 247 | 0.003180 | 0.009610 | -0.002994 | -0.006210 | 0.012570 |
| next_next_close | eq_fresh | domestic | 257 | -0.001163 | -0.001617 | -0.000727 | -0.002243 | -0.000084 |
| next_next_close | eq_lag1 | eq_fresh | 257 | 0.003670 | 0.005684 | 0.001732 | -0.001482 | 0.008821 |
| next_next_close | eq_lag17 | eq_fresh | 257 | 0.000405 | 0.001340 | -0.000494 | -0.002300 | 0.003111 |
| next_next_close | eq_lag2 | eq_fresh | 257 | 0.001350 | 0.002013 | 0.000713 | -0.001624 | 0.004324 |
| next_next_close | eq_lag5 | eq_fresh | 257 | 0.000224 | -0.001254 | 0.001646 | -0.004995 | 0.005443 |
| next_next_close | eq_smooth | eq_fresh | 257 | 0.000534 | 0.002838 | -0.001683 | -0.003809 | 0.004877 |
| next_next_close | gift_conditional | domestic | 247 | -0.000188 | 0.002153 | -0.002437 | -0.005553 | 0.005177 |
| two | eq_fresh | domestic | 257 | 0.005454 | 0.004507 | 0.006364 | -0.003843 | 0.014750 |
| two | eq_lag1 | eq_fresh | 257 | -0.006552 | -0.007010 | -0.006112 | -0.017956 | 0.004851 |
| two | eq_lag17 | eq_fresh | 257 | -0.005762 | -0.004873 | -0.006618 | -0.014732 | 0.003207 |
| two | eq_lag2 | eq_fresh | 257 | -0.006098 | -0.003547 | -0.008552 | -0.017526 | 0.005329 |
| two | eq_lag5 | eq_fresh | 257 | -0.006406 | -0.007449 | -0.005402 | -0.015952 | 0.003141 |
| two | eq_smooth | eq_fresh | 257 | -0.005678 | -0.005456 | -0.005892 | -0.015389 | 0.004033 |
| two | gift_conditional | domestic | 247 | 0.021906 | 0.028351 | 0.015717 | 0.008571 | 0.035241 |
| three | eq_fresh | domestic | 256 | -0.001672 | -0.001116 | -0.002211 | -0.005329 | 0.001985 |
| three | eq_lag1 | eq_fresh | 256 | 0.001248 | 0.000524 | 0.001949 | -0.004373 | 0.006869 |
| three | eq_lag17 | eq_fresh | 256 | 0.001154 | -0.000787 | 0.003036 | -0.002560 | 0.004868 |
| three | eq_lag2 | eq_fresh | 256 | 0.001442 | 0.000483 | 0.002372 | -0.003592 | 0.006476 |
| three | eq_lag5 | eq_fresh | 256 | 0.000974 | 0.000487 | 0.001445 | -0.003822 | 0.005769 |
| three | eq_smooth | eq_fresh | 256 | 0.000758 | 0.000069 | 0.001426 | -0.004777 | 0.006293 |
| three | gift_conditional | domestic | 246 | 0.014894 | 0.018460 | 0.011442 | 0.004535 | 0.025253 |
| five | eq_fresh | domestic | 265 | -0.000355 | 0.000659 | -0.002263 | -0.003403 | 0.002693 |
| five | eq_lag1 | eq_fresh | 265 | 0.000539 | 0.000072 | 0.001417 | -0.003618 | 0.004695 |
| five | eq_lag17 | eq_fresh | 265 | -0.001209 | -0.002210 | 0.000674 | -0.005306 | 0.002889 |
| five | eq_lag2 | eq_fresh | 265 | 0.001931 | 0.001797 | 0.002182 | -0.002718 | 0.006579 |
| five | eq_lag5 | eq_fresh | 265 | 0.001081 | 0.000189 | 0.002758 | -0.003592 | 0.005754 |
| five | eq_smooth | eq_fresh | 265 | 0.000852 | 0.000577 | 0.001369 | -0.003500 | 0.005204 |
| five | gift_conditional | domestic | 253 | 0.005509 | 0.008358 | 0.000074 | -0.006691 | 0.017710 |
| ten | eq_fresh | domestic | 249 | -0.001801 | -0.001261 | -0.002353 | -0.004661 | 0.001059 |
| ten | eq_lag1 | eq_fresh | 249 | 0.002777 | 0.002026 | 0.003545 | -0.001451 | 0.007004 |
| ten | eq_lag17 | eq_fresh | 249 | 0.001679 | 0.002266 | 0.001076 | -0.001475 | 0.004833 |
| ten | eq_lag2 | eq_fresh | 249 | 0.000832 | -0.000236 | 0.001926 | -0.001861 | 0.003526 |
| ten | eq_lag5 | eq_fresh | 249 | 0.001742 | 0.000998 | 0.002504 | -0.002138 | 0.005622 |
| ten | eq_smooth | eq_fresh | 249 | 0.001030 | -0.000620 | 0.002720 | -0.004193 | 0.006253 |
| ten | gift_conditional | domestic | 241 | 0.005662 | 0.005760 | 0.005562 | -0.002701 | 0.014024 |
| twentyone | eq_fresh | domestic | 217 | 0.000071 | 0.000015 | 0.000176 | -0.000977 | 0.001120 |
| twentyone | eq_lag1 | eq_fresh | 217 | 0.000188 | 0.000508 | -0.000406 | -0.001257 | 0.001633 |
| twentyone | eq_lag17 | eq_fresh | 217 | 0.000268 | 0.000057 | 0.000658 | -0.002212 | 0.002747 |
| twentyone | eq_lag2 | eq_fresh | 217 | -0.000641 | -0.000744 | -0.000451 | -0.002231 | 0.000948 |
| twentyone | eq_lag5 | eq_fresh | 217 | -0.000778 | -0.000733 | -0.000862 | -0.002630 | 0.001074 |
| twentyone | eq_smooth | eq_fresh | 217 | -0.000841 | -0.000727 | -0.001052 | -0.002328 | 0.000647 |
| twentyone | gift_conditional | domestic | 210 | 0.000794 | -0.000990 | 0.004143 | -0.017558 | 0.019146 |

## Matched after opening and after the first hour

| cutoff | target | candidate | control | n | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 09:25 | regular_after_bar | eq_fresh | cash_prefix | 257 | -0.000007 | -0.000025 | 0.000010 |
| 09:25 | regular_after_bar | foreign_after_gap | breadth_after_open | 257 | -0.000015 | -0.000044 | 0.000015 |
| 09:25 | regular_after_bar | rich_fresh | eq_fresh | 257 | -0.000041 | -0.000120 | 0.000037 |
| 09:25 | firsthour_residual | eq_fresh | cash_prefix | 257 | -0.000004 | -0.000008 | -0.000001 |
| 09:25 | firsthour_residual | foreign_after_gap | breadth_after_open | 257 | -0.000012 | -0.000026 | 0.000002 |
| 09:25 | firsthour_residual | rich_fresh | eq_fresh | 257 | -0.000034 | -0.000079 | 0.000011 |
| 09:25 | next_gap | eq_fresh | cash_prefix | 256 | 0.000003 | -0.000025 | 0.000032 |
| 09:25 | next_gap | foreign_after_gap | breadth_after_open | 256 | -0.000009 | -0.000053 | 0.000036 |
| 09:25 | next_gap | rich_fresh | eq_fresh | 256 | -0.000083 | -0.000238 | 0.000073 |
| 09:25 | five | eq_fresh | cash_prefix | 263 | -0.000005 | -0.000030 | 0.000020 |
| 09:25 | five | foreign_after_gap | breadth_after_open | 263 | 0.000070 | -0.000046 | 0.000187 |
| 09:25 | five | rich_fresh | eq_fresh | 263 | 0.000093 | -0.000396 | 0.000583 |
| 10:20 | remaining | eq_fresh | cash_prefix | 257 | -0.000005 | -0.000018 | 0.000009 |
| 10:20 | remaining | foreign_after_gap | breadth_after_open | 257 | -0.000010 | -0.000036 | 0.000016 |
| 10:20 | remaining | rich_fresh | eq_fresh | 257 | -0.000039 | -0.000131 | 0.000052 |
| 10:20 | next_gap | eq_fresh | cash_prefix | 256 | 0.000002 | -0.000028 | 0.000032 |
| 10:20 | next_gap | foreign_after_gap | breadth_after_open | 256 | -0.000009 | -0.000044 | 0.000025 |
| 10:20 | next_gap | rich_fresh | eq_fresh | 256 | -0.000084 | -0.000232 | 0.000063 |
| 10:20 | five | eq_fresh | cash_prefix | 263 | -0.000007 | -0.000031 | 0.000017 |
| 10:20 | five | foreign_after_gap | breadth_after_open | 263 | 0.000072 | -0.000059 | 0.000203 |
| 10:20 | five | rich_fresh | eq_fresh | 263 | 0.000054 | -0.000488 | 0.000596 |

## Regional availability and age

| target | candidate | control | n | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- |
| gap | asia_fresh | domestic | 258 | -0.000390 | -0.012702 | 0.011923 |
| gap | asia_stale | asia_fresh | 258 | 0.000586 | -0.012815 | 0.013986 |
| gap | europe_fresh | domestic | 258 | 0.010858 | -0.004620 | 0.026337 |
| gap | europe_stale | europe_fresh | 258 | -0.007892 | -0.030512 | 0.014727 |
| gap | us_fresh | domestic | 258 | 0.028738 | 0.000788 | 0.056688 |
| gap | us_stale | us_fresh | 258 | -0.029233 | -0.058708 | 0.000241 |
| regular | asia_fresh | domestic | 258 | 0.000041 | -0.004453 | 0.004535 |
| regular | asia_stale | asia_fresh | 258 | -0.000138 | -0.006188 | 0.005911 |
| regular | europe_fresh | domestic | 258 | 0.000624 | -0.002392 | 0.003639 |
| regular | europe_stale | europe_fresh | 258 | -0.001398 | -0.004702 | 0.001907 |
| regular | us_fresh | domestic | 258 | 0.000394 | -0.001459 | 0.002246 |
| regular | us_stale | us_fresh | 258 | -0.000717 | -0.003421 | 0.001988 |
| one | asia_fresh | domestic | 258 | 0.002587 | -0.004333 | 0.009507 |
| one | asia_stale | asia_fresh | 258 | -0.000358 | -0.009413 | 0.008697 |
| one | europe_fresh | domestic | 258 | 0.000027 | -0.005251 | 0.005305 |
| one | europe_stale | europe_fresh | 258 | 0.001257 | -0.004703 | 0.007217 |
| one | us_fresh | domestic | 258 | 0.005059 | -0.008976 | 0.019095 |
| one | us_stale | us_fresh | 258 | -0.004765 | -0.018716 | 0.009187 |
| five | asia_fresh | domestic | 265 | -0.000534 | -0.001581 | 0.000513 |
| five | asia_stale | asia_fresh | 265 | 0.001715 | -0.000627 | 0.004057 |
| five | europe_fresh | domestic | 265 | 0.000618 | -0.002764 | 0.004000 |
| five | europe_stale | europe_fresh | 265 | 0.000384 | -0.004598 | 0.005366 |
| five | us_fresh | domestic | 265 | -0.000589 | -0.005625 | 0.004447 |
| five | us_stale | us_fresh | 265 | 0.001251 | -0.005250 | 0.007752 |
| twentyone | asia_fresh | domestic | 217 | -0.000304 | -0.001990 | 0.001383 |
| twentyone | asia_stale | asia_fresh | 217 | -0.000273 | -0.002529 | 0.001982 |
| twentyone | europe_fresh | domestic | 217 | 0.000248 | -0.001045 | 0.001541 |
| twentyone | europe_stale | europe_fresh | 217 | -0.000371 | -0.002247 | 0.001505 |
| twentyone | us_fresh | domestic | 217 | -0.000239 | -0.002032 | 0.001554 |
| twentyone | us_stale | us_fresh | 217 | -0.000309 | -0.001870 | 0.001252 |

The close-to-close target includes the overnight component, so a modest close-to-close gain can arise mainly from the better opening distribution. The remaining cash-session return is separately scored after its reference price has been observed. Original five- and 21-session support matches the frozen earlier/later cohorts. The adjusted confidence bands reflect the reported V16 comparisons on this panel.

[All decay regressions by cutoff and target](session-leaderboard.csv) · [Per-case 08:55 forecasts](decay-0855-scores.csv.gz) · [Post-opening 09:25 forecasts](decay-0925-scores.csv.gz) · [10:20 forecasts](decay-1020-scores.csv.gz) · [Matched decay evidence](session-matched-evidence.csv)
