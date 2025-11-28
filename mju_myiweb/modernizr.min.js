window.Modernizr=function(ay,ax,aw){function U(b){ao.cssText=b}function T(d,c){return U(ak.join(d+";")+(c||""))
}function S(d,c){return typeof d===c}function R(d,c){return !!~(""+d).indexOf(c)}function Q(f,c){for(var h in f){var g=f[h];
if(!R(g,"-")&&ao[g]!==aw){return c=="pfx"?g:!0}}return !1}function P(g,c,j){for(var i in g){var h=c[g[i]];
if(h!==aw){return j===!1?g[i]:S(h,"function")?h.bind(j||c):h}}return !1}function O(g,f,j){var i=g.charAt(0).toUpperCase()+g.slice(1),h=(g+" "+ai.join(i+" ")+i).split(" ");
return S(f,"string")||S(f,"undefined")?Q(h,f):(h=(g+" "+ah.join(i+" ")+i).split(" "),P(h,f,j))
}function N(){au.input=function(f){for(var b=0,a=f.length;b<a;b++){ad[f[b]]=f[b] in an
}return ad.list&&(ad.list=!!ax.createElement("datalist")&&!!ay.HTMLDataListElement),ad
}("autocomplete autofocus list placeholder max min multiple pattern required step".split(" ")),au.inputtypes=function(b){for(var l=0,k,j,g,c=b.length;
l<c;l++){an.setAttribute("type",j=b[l]),k=an.type!=="text",k&&(an.value=am,an.style.cssText="position:absolute;visibility:hidden;",/^range$/.test(j)&&an.style.WebkitAppearance!==aw?(ar.appendChild(an),g=ax.defaultView,k=g.getComputedStyle&&g.getComputedStyle(an,null).WebkitAppearance!=="textfield"&&an.offsetHeight!==0,ar.removeChild(an)):/^(search|tel)$/.test(j)||(/^(url|email)$/.test(j)?k=an.checkValidity&&an.checkValidity()===!1:k=an.value!=am)),ae[b[l]]=!!k
}return ae}("search tel url email datetime date month week time datetime-local number range color".split(" "))
}var av="2.6.2",au={},at=!0,ar=ax.documentElement,aq="modernizr",ap=ax.createElement(aq),ao=ap.style,an=ax.createElement("input"),am=":)",al={}.toString,ak=" -webkit- -moz- -o- -ms- ".split(" "),aj="Webkit Moz O ms",ai=aj.split(" "),ah=aj.toLowerCase().split(" "),ag={svg:"http://www.w3.org/2000/svg"},af={},ae={},ad={},ac=[],ab=ac.slice,aa,Z=function(v,u,t,s){var r,q,p,o,h=ax.createElement("div"),g=ax.body,b=g||ax.createElement("body");
if(parseInt(t,10)){while(t--){p=ax.createElement("div"),p.id=s?s[t]:aq+(t+1),h.appendChild(p)
}}return r=["&#173;",'<style id="s',aq,'">',v,"</style>"].join(""),h.id=aq,(g?h:b).innerHTML+=r,b.appendChild(h),g||(b.style.background="",b.style.overflow="hidden",o=ar.style.overflow,ar.style.overflow="hidden",ar.appendChild(b)),q=u(h,v),g?h.parentNode.removeChild(h):(b.parentNode.removeChild(b),ar.style.overflow=o),!!q
},Y=function(a){var f=ay.matchMedia||ay.msMatchMedia;if(f){return f(a).matches}var e;
return Z("@media "+a+" { #"+aq+" { position: absolute; } }",function(c){e=(ay.getComputedStyle?getComputedStyle(c,null):c.currentStyle)["position"]=="absolute"
}),e},X=function(){function c(h,g){g=g||ax.createElement(b[h]||"div"),h="on"+h;var a=h in g;
return a||(g.setAttribute||(g=ax.createElement("div")),g.setAttribute&&g.removeAttribute&&(g.setAttribute(h,""),a=S(g[h],"function"),S(g[h],"undefined")||(g[h]=aw),g.removeAttribute(h))),g=null,a
}var b={select:"input",change:"input",submit:"form",reset:"form",error:"img",load:"img",abort:"img"};
return c}(),W={}.hasOwnProperty,V;!S(W,"undefined")&&!S(W.call,"undefined")?V=function(d,c){return W.call(d,c)
}:V=function(d,c){return c in d&&S(d.constructor.prototype[c],"undefined")},Function.prototype.bind||(Function.prototype.bind=function(a){var h=this;
if(typeof h!="function"){throw new TypeError}var g=ab.call(arguments,1),f=function(){if(this instanceof f){var b=function(){};
b.prototype=h.prototype;var d=new b,c=h.apply(d,g.concat(ab.call(arguments)));return Object(c)===c?c:d
}return h.apply(a,g.concat(ab.call(arguments)))};return f}),af.flexbox=function(){return O("flexWrap")
},af.flexboxlegacy=function(){return O("boxDirection")},af.canvas=function(){var b=ax.createElement("canvas");
return !!b.getContext&&!!b.getContext("2d")},af.canvastext=function(){return !!au.canvas&&!!S(ax.createElement("canvas").getContext("2d").fillText,"function")
},af.webgl=function(){return !!ay.WebGLRenderingContext},af.touch=function(){var a;
return"ontouchstart" in ay||ay.DocumentTouch&&ax instanceof DocumentTouch?a=!0:Z(["@media (",ak.join("touch-enabled),("),aq,")","{#modernizr{top:9px;position:absolute}}"].join(""),function(b){a=b.offsetTop===9
}),a},af.geolocation=function(){return"geolocation" in navigator},af.postmessage=function(){return !!ay.postMessage
},af.websqldatabase=function(){return !!ay.openDatabase},af.indexedDB=function(){return !!O("indexedDB",ay)
},af.hashchange=function(){return X("hashchange",ay)&&(ax.documentMode===aw||ax.documentMode>7)
},af.history=function(){return !!ay.history&&!!history.pushState},af.draganddrop=function(){var b=ax.createElement("div");
return"draggable" in b||"ondragstart" in b&&"ondrop" in b},af.websockets=function(){return"WebSocket" in ay||"MozWebSocket" in ay
},af.rgba=function(){return U("background-color:rgba(150,255,150,.5)"),R(ao.backgroundColor,"rgba")
},af.hsla=function(){return U("background-color:hsla(120,40%,100%,.5)"),R(ao.backgroundColor,"rgba")||R(ao.backgroundColor,"hsla")
},af.multiplebgs=function(){return U("background:url(https://),url(https://),red url(https://)"),/(url\s*\(.*?){3}/.test(ao.background)
},af.backgroundsize=function(){return O("backgroundSize")},af.borderimage=function(){return O("borderImage")
},af.borderradius=function(){return O("borderRadius")},af.boxshadow=function(){return O("boxShadow")
},af.textshadow=function(){return ax.createElement("div").style.textShadow===""},af.opacity=function(){return T("opacity:.55"),/^0.55$/.test(ao.opacity)
},af.cssanimations=function(){return O("animationName")},af.csscolumns=function(){return O("columnCount")
},af.cssgradients=function(){var e="background-image:",d="gradient(linear,left top,right bottom,from(#9f9),to(white));",f="linear-gradient(left top,#9f9, white);";
return U((e+"-webkit- ".split(" ").join(d+e)+ak.join(f+e)).slice(0,-e.length)),R(ao.backgroundImage,"gradient")
},af.cssreflections=function(){return O("boxReflect")},af.csstransforms=function(){return !!O("transform")
},af.csstransforms3d=function(){var b=!!O("perspective");return b&&"webkitPerspective" in ar.style&&Z("@media (transform-3d),(-webkit-transform-3d){#modernizr{left:9px;position:absolute;height:3px;}}",function(a,d){b=a.offsetLeft===9&&a.offsetHeight===3
}),b},af.csstransitions=function(){return O("transition")},af.fontface=function(){var b;
return Z('@font-face {font-family:"font";src:url("https://")}',function(k,j){var i=ax.getElementById("smodernizr"),h=i.sheet||i.styleSheet,a=h?h.cssRules&&h.cssRules[0]?h.cssRules[0].cssText:h.cssText||"":"";
b=/src/i.test(a)&&a.indexOf(j.split(" ")[0])===0}),b},af.generatedcontent=function(){var b;
return Z(["#",aq,"{font:0/0 a}#",aq,':after{content:"',am,'";visibility:hidden;font:3px/1 a}'].join(""),function(a){b=a.offsetHeight>=3
}),b},af.video=function(){var b=ax.createElement("video"),f=!1;try{if(f=!!b.canPlayType){f=new Boolean(f),f.ogg=b.canPlayType('video/ogg; codecs="theora"').replace(/^no$/,""),f.h264=b.canPlayType('video/mp4; codecs="avc1.42E01E"').replace(/^no$/,""),f.webm=b.canPlayType('video/webm; codecs="vp8, vorbis"').replace(/^no$/,"")
}}catch(e){}return f},af.audio=function(){var b=ax.createElement("audio"),f=!1;try{if(f=!!b.canPlayType){f=new Boolean(f),f.ogg=b.canPlayType('audio/ogg; codecs="vorbis"').replace(/^no$/,""),f.mp3=b.canPlayType("audio/mpeg;").replace(/^no$/,""),f.wav=b.canPlayType('audio/wav; codecs="1"').replace(/^no$/,""),f.m4a=(b.canPlayType("audio/x-m4a;")||b.canPlayType("audio/aac;")).replace(/^no$/,"")
}}catch(e){}return f},af.localstorage=function(){try{return localStorage.setItem(aq,aq),localStorage.removeItem(aq),!0
}catch(b){return !1}},af.sessionstorage=function(){try{return sessionStorage.setItem(aq,aq),sessionStorage.removeItem(aq),!0
}catch(b){return !1}},af.webworkers=function(){return !!ay.Worker},af.applicationcache=function(){return !!ay.applicationCache
},af.svg=function(){return !!ax.createElementNS&&!!ax.createElementNS(ag.svg,"svg").createSVGRect
},af.inlinesvg=function(){var b=ax.createElement("div");return b.innerHTML="<svg/>",(b.firstChild&&b.firstChild.namespaceURI)==ag.svg
},af.smil=function(){return !!ax.createElementNS&&/SVGAnimate/.test(al.call(ax.createElementNS(ag.svg,"animate")))
},af.svgclippaths=function(){return !!ax.createElementNS&&/SVGClipPath/.test(al.call(ax.createElementNS(ag.svg,"clipPath")))
};for(var M in af){V(af,M)&&(aa=M.toLowerCase(),au[aa]=af[M](),ac.push((au[aa]?"":"no-")+aa))
}return au.input||N(),au.addTest=function(e,c){if(typeof e=="object"){for(var f in e){V(e,f)&&au.addTest(f,e[f])
}}else{e=e.toLowerCase();if(au[e]!==aw){return au}c=typeof c=="function"?c():c,typeof at!="undefined"&&at&&(ar.className+=" "+(c?"":"no-")+e),au[e]=c
}return au},U(""),ap=an=null,au._version=av,au._prefixes=ak,au._domPrefixes=ah,au._cssomPrefixes=ai,au.mq=Y,au.hasEvent=X,au.testProp=function(b){return Q([b])
},au.testAllProps=O,au.testStyles=Z,ar.className=ar.className.replace(/(^|\s)no-js(\s|$)/,"$1$2")+(at?" js "+ac.join(" "):""),au
}(this,this.document),function(Z,Y){function P(f,e){var h=f.createElement("p"),g=f.getElementsByTagName("head")[0]||f.documentElement;
return h.innerHTML="x<style>"+e+"</style>",g.insertBefore(h.lastChild,g.firstChild)
}function O(){var b=I.elements;return typeof b=="string"?b.split(" "):b}function N(d){var c=R[d[T]];
return c||(c={},S++,d[T]=S,R[S]=c),c}function M(b,h,e){h||(h=Y);if(Q){return h.createElement(b)
}e||(e=N(h));var d;return e.cache[b]?d=e.cache[b].cloneNode():V.test(b)?d=(e.cache[b]=e.createElem(b)).cloneNode():d=e.createElem(b),d.canHaveChildren&&!W.test(b)?e.frag.appendChild(d):d
}function L(b,l){b||(b=Y);if(Q){return b.createDocumentFragment()}l=l||N(b);var k=l.frag.cloneNode(),j=0,i=O(),h=i.length;
for(;j<h;j++){k.createElement(i[j])}return k}function K(d,c){c.cache||(c.cache={},c.createElem=d.createElement,c.createFrag=d.createDocumentFragment,c.frag=c.createFrag()),d.createElement=function(a){return I.shivMethods?M(a,d,c):c.createElem(a)
},d.createDocumentFragment=Function("h,f","return function(){var n=f.cloneNode(),c=n.createElement;h.shivMethods&&("+O().join().replace(/\w+/g,function(b){return c.createElem(b),c.frag.createElement(b),'c("'+b+'")'
})+");return n}")(I,c.frag)}function J(b){b||(b=Y);var d=N(b);return I.shivCSS&&!U&&!d.hasCSS&&(d.hasCSS=!!P(b,"article,aside,figcaption,figure,footer,header,hgroup,nav,section{display:block}mark{background:#FF0;color:#000}")),Q||K(b,d),b
}function E(h){var g,l=h.getElementsByTagName("*"),k=l.length,j=RegExp("^(?:"+O().join("|")+")$","i"),i=[];
while(k--){g=l[k],j.test(g.nodeName)&&i.push(g.applyElement(D(g)))}return i}function D(g){var f,j=g.attributes,i=j.length,h=g.ownerDocument.createElement(G+":"+g.nodeName);
while(i--){f=j[i],f.specified&&h.setAttribute(f.nodeName,f.nodeValue)}return h.style.cssText=g.style.cssText,h
}function C(h){var g,l=h.split("{"),k=l.length,j=RegExp("(^|[\\s,>+~])("+O().join("|")+")(?=[[\\s,>+~#.:]|$)","gi"),i="$1"+G+"\\:$2";
while(k--){g=l[k]=l[k].split("}"),g[g.length-1]=g[g.length-1].replace(j,i),l[k]=g.join("}")
}return l.join("{")}function B(d){var c=d.length;while(c--){d[c].removeNode()}}function A(i){function j(){clearTimeout(m._removeSheetTimer),h&&h.removeNode(!0),h=null
}var h,n,m=N(i),l=i.namespaces,k=i.parentWindow;return !F||i.printShived?i:(typeof l[G]=="undefined"&&l.add(G),k.attachEvent("onbeforeprint",function(){j();
var r,q,p,o=i.styleSheets,g=[],c=o.length,b=Array(c);while(c--){b[c]=o[c]}while(p=b.pop()){if(!p.disabled&&H.test(p.media)){try{r=p.imports,q=r.length
}catch(a){q=0}for(c=0;c<q;c++){b.push(r[c])}try{g.push(p.cssText)}catch(a){}}}g=C(g.reverse().join("")),n=E(i),h=P(i,g)
}),k.attachEvent("onafterprint",function(){B(n),clearTimeout(m._removeSheetTimer),m._removeSheetTimer=setTimeout(j,500)
}),i.printShived=!0,i)}var X=Z.html5||{},W=/^<|^(?:button|map|select|textarea|object|iframe|option|optgroup)$/i,V=/^<|^(?:a|b|button|code|div|fieldset|form|h1|h2|h3|h4|h5|h6|i|iframe|img|input|label|li|link|ol|option|p|param|q|script|select|span|strong|style|table|tbody|td|textarea|tfoot|th|thead|tr|ul)$/i,U,T="_html5shiv",S=0,R={},Q;
(function(){try{var b=Y.createElement("a");b.innerHTML="<xyz></xyz>",U="hidden" in b,Q=b.childNodes.length==1||function(){Y.createElement("a");
var c=Y.createDocumentFragment();return typeof c.cloneNode=="undefined"||typeof c.createDocumentFragment=="undefined"||typeof c.createElement=="undefined"
}()}catch(d){U=!0,Q=!0}})();var I={elements:X.elements||"abbr article aside audio bdi canvas data datalist details figcaption figure footer header hgroup mark meter nav output progress section summary time video",shivCSS:X.shivCSS!==!1,supportsUnknownElements:Q,shivMethods:X.shivMethods!==!1,type:"default",shivDocument:J,createElement:M,createDocumentFragment:L};
Z.html5=I,J(Y);var H=/^$|\b(?:all|print)\b/,G="html5shiv",F=!Q&&function(){var a=Y.documentElement;
return typeof Y.namespaces!="undefined"&&typeof Y.parentWindow!="undefined"&&typeof a.applyElement!="undefined"&&typeof a.removeNode!="undefined"&&typeof Z.attachEvent!="undefined"
}();I.type+=" print",I.shivPrint=A,A(Y)}(this,document),function(ad,ac,ab){function aa(b){return"[object Function]"==P.call(b)
}function Z(b){return"string"==typeof b}function Y(){}function X(b){return !b||"loaded"==b||"complete"==b||"uninitialized"==b
}function W(){var b=O.shift();M=1,b?b.t?R(function(){("c"==b.t?L.injectCss:L.injectJs)(b.s,0,b.a,b.x,b.e,1)
},0):(b(),W()):M=0}function V(w,v,t,s,q,p,n){function m(a){if(!g&&X(h.readyState)&&(x.r=g=1,!M&&W(),h.onload=h.onreadystatechange=null,a)){"img"!=w&&R(function(){I.removeChild(h)
},50);for(var c in D[v]){D[v].hasOwnProperty(c)&&D[v][c].onload()}}}var n=n||L.errorTimeout,h=ac.createElement(w),g=0,b=0,x={t:t,s:v,e:q,a:p,x:n};
1===D[v]&&(b=1,D[v]=[]),"object"==w?h.data=v:(h.src=v,h.type=w),h.width=h.height="0",h.onerror=h.onload=h.onreadystatechange=function(){m.call(this,b)
},O.splice(s,0,x),"img"!=w&&(b||2===D[v]?(I.insertBefore(h,J?null:Q),R(m,n)):D[v].push(h))
}function U(g,e,j,i,h){return M=0,e=e||"j",Z(g)?V("c"==e?G:H,g,e,this.i++,j,i,h):(O.splice(this.i++,0,g),1==O.length&&W()),this
}function T(){var b=L;return b.loader={load:U,i:0},b}var S=ac.documentElement,R=ad.setTimeout,Q=ac.getElementsByTagName("script")[0],P={}.toString,O=[],M=0,K="MozAppearance" in S.style,J=K&&!!ac.createRange().compareNode,I=J?S:Q.parentNode,S=ad.opera&&"[object Opera]"==P.call(ad.opera),S=!!ac.attachEvent&&!S,H=K?"object":S?"script":"img",G=S?"script":H,F=Array.isArray||function(b){return"[object Array]"==P.call(b)
},E=[],D={},C={timeout:function(d,c){return c.length&&(d.timeout=c[0]),d}},N,L;L=function(e){function c(i){var i=i.split("!"),h=E.length,q=i.pop(),p=i.length,q={url:q,origUrl:q,prefixes:i},o,l,j;
for(l=0;l<p;l++){j=i[l].split("="),(o=C[j.shift()])&&(q=o(q,j))}for(l=0;l<h;l++){q=E[l](q)
}return q}function n(b,s,r,q,p){var o=c(b),l=o.autoCallback;o.url.split(".").pop().split("?").shift(),o.bypass||(s&&(s=aa(s)?s:s[b]||s[q]||s[b.split("/").pop().split("?")[0]]),o.instead?o.instead(b,s,r,q,p):(D[o.url]?o.noexec=!0:D[o.url]=1,r.load(o.url,o.forceCSS||!o.forceJS&&"css"==o.url.split(".").pop().split("?").shift()?"c":ab,o.noexec,o.attrs,o.timeout),(aa(s)||aa(l))&&r.load(function(){T(),s&&s(o.origUrl,p,q),l&&l(o.origUrl,p,q),D[o.url]=2
})))}function m(w,v){function u(b,h){if(b){if(Z(b)){h||(r=function(){var i=[].slice.call(arguments);
q.apply(this,i),p()}),n(b,r,v,0,t)}else{if(Object(b)===b){for(g in o=function(){var a=0,i;
for(i in b){b.hasOwnProperty(i)&&a++}return a}(),b){b.hasOwnProperty(g)&&(!h&&!--o&&(aa(r)?r=function(){var i=[].slice.call(arguments);
q.apply(this,i),p()}:r[g]=function(i){return function(){var a=[].slice.call(arguments);
i&&i.apply(this,a),p()}}(q[g])),n(b[g],r,v,g,t))}}}}else{!h&&p()}}var t=!!w.test,s=w.load||w.both,r=w.callback||Y,q=r,p=w.complete||Y,o,g;
u(t?w.yep:w.nope,!!s),s&&u(s)}var k,f,d=this.yepnope.loader;if(Z(e)){n(e,0,d,0)}else{if(F(e)){for(k=0;
k<e.length;k++){f=e[k],Z(f)?n(f,0,d,0):F(f)?L(f):Object(f)===f&&m(f,d)}}else{Object(e)===e&&m(e,d)
}}},L.addPrefix=function(d,c){C[d]=c},L.addFilter=function(b){E.push(b)},L.errorTimeout=10000,null==ac.readyState&&ac.addEventListener&&(ac.readyState="loading",ac.addEventListener("DOMContentLoaded",N=function(){ac.removeEventListener("DOMContentLoaded",N,0),ac.readyState="complete"
},0)),ad.yepnope=T(),ad.yepnope.executeStack=W,ad.yepnope.injectJs=function(r,q,p,n,m,h){var g=ac.createElement("script"),f,b,n=n||L.errorTimeout;
g.src=r;for(b in p){g.setAttribute(b,p[b])}q=h?W:q||Y,g.onreadystatechange=g.onload=function(){!f&&X(g.readyState)&&(f=1,q(),g.onload=g.onreadystatechange=null)
},R(function(){f||(f=1,q(1))},n),m?g.onload():Q.parentNode.insertBefore(g,Q)},ad.yepnope.injectCss=function(b,n,m,l,k,h){var l=ac.createElement("link"),f,n=h?W:n||Y;
l.href=b,l.rel="stylesheet",l.type="text/css";for(f in m){l.setAttribute(f,m[f])}k||(Q.parentNode.insertBefore(l,Q),R(n,0))
}}(this,document),Modernizr.load=function(){yepnope.apply(window,[].slice.call(arguments,0))
};