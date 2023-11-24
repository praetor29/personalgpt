import { memo } from "react";
import { GlHeader } from "gitlanding/GlHeader";
import { GlLogo } from "gitlanding/utils/GlLogo"; // import logo module
import { declareComponentKeys, useTranslation } from "i18n";

// Import the useIsDarkModeEnabled hook from onyxia-ui (custom!!)
import { useIsDarkModeEnabled } from 'onyxia-ui/lib/useIsDarkModeEnabled';

import { routes } from "router";
// import { declareComponentKeys, useTranslation, useLang } from "i18n"; // lanuage removed

// import { createLanguageSelect } from "onyxia-ui/LanguageSelect";
// import type { Language } from "i18n";

// const { LanguageSelect } = createLanguageSelect<Language>({
// 	"languagesPrettyPrint": {
// 		"en": "English",
// 		"fr": "Francais"
// 	}
// })

// import banners
import lightBanner from "assets/icons/personalgpt/banner/light.png";
import darkBanner from "assets/icons/personalgpt/banner/dark.png";


export const Header = memo(() => {
	const { t } = useTranslation({ Header })
	const { isDarkModeEnabled } = useIsDarkModeEnabled(); // custom!!
	
	// light vs dark saga (custom!!)
	const banner = isDarkModeEnabled ? darkBanner : lightBanner;

	// const { lang, setLang } = useLang();
	return <GlHeader
		// title={<a {...routes.home().link}><h1>{t("headerTitle")}</h1></a>}
		title={
			<a {...routes.home().link}>
				<GlLogo logoUrl={banner} width={200} />
			</a>
		}
		links={[
			{
				"label": t("link1label"),
				"href": "https://discord.gg/9EA2mrG3ZT",
			},
			{
				"label": t("link2label"),
				"href": "https://github.com/praetor29/personalgpt/",
			},
		]}
		enableDarkModeSwitch={true}
		githubRepoUrl="https://github.com/praetor29/personalgpt/"
		showGithubStarCount={true}
		githubButtonSize="large"

		// customItemEnd={{
		// 	"item": <LanguageSelect
		// 		language={lang}
		// 		onLanguageChange={setLang}
		// 		variant="big"
		// 	/>
		// }}

	/>
});

export const { i18n } = declareComponentKeys<
	// | "headerTitle"
	| "link1label"
	| "link2label"
>()({ Header });
