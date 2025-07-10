import { g as getContext } from './ssr-B2uXEC_g.js';
import './exports-Cu4i9J_Z.js';

function e(t,s=JSON.parse){try{return s(sessionStorage[t])}catch{}}const o="sveltekit:snapshot",n="sveltekit:scroll";e(n);e(o);const i=()=>{const t=getContext("__svelte__");return {page:{subscribe:t.page.subscribe},navigating:{subscribe:t.navigating.subscribe},updated:t.updated}},b={subscribe(t){return i().page.subscribe(t)}};

export { b };
//# sourceMappingURL=stores-DAOnrvrO.js.map
