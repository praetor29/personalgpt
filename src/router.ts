
import {createRouter, defineRoute} from "type-route";
import {makeThisModuleAnExecutableRouteLister} from "github-pages-plugin-for-type-route";


export const routeDefs = {
    "home": defineRoute("/personalgpt"),
    "FourOhFour": defineRoute("/404"),
};

makeThisModuleAnExecutableRouteLister(routeDefs);

export const {RouteProvider, routes, useRoute} = createRouter(
	routeDefs
);


