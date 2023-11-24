import { memo } from "react";
import { GlFooter } from "gitlanding/GlFooter";
// import { routes } from "router"; // removed example page
import { declareComponentKeys, useTranslation } from "i18n";


export const Footer = memo(() => {
	const { t } = useTranslation({ Footer })
	return <GlFooter
		bottomDivContent={t("license")}
		// email="pranavchip@gmail.com"
		// phoneNumber="+33545345676"
		links={[
			// {
			// 	"label": t("link1label"),
			// 	...routes.pageExample().link
			// }, // removed example page
			{
				"label": t("link1label"),
				"href": "https://discord.gg/9EA2mrG3ZT",
			},
			{
				"label": t("link2label"),
				"href": "https://github.com/praetor29/personalgpt/",
			},
		]}
	/>
})

export const { i18n } = declareComponentKeys<
	| "license"
	| "link1label"
	| "link2label"
>()({ Footer });
