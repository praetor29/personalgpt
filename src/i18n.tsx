import { createI18nApi, declareComponentKeys } from "i18nifty";
export { declareComponentKeys };

//List the languages you with to support
export const languages = ["en"] as const;

//If the user's browser language doesn't match any 
//of the languages above specify the language to fallback to:  
export const fallbackLanguage = "en";

export type Language = typeof languages[number];

export type LocalizedString = Parameters<typeof resolveLocalizedString>[0];

export const { 
	useTranslation, 
	resolveLocalizedString, 
	useLang, 
	$lang,
	useResolveLocalizedString,
	/** For use outside of React */
	getTranslation 
} = createI18nApi<
    | typeof import ("pages/Home").i18n
    | typeof import ("App/Header").i18n
		| typeof import ("App/Footer").i18n
		| typeof import ("pages/FourOFour").i18n
>()(
    { languages, fallbackLanguage },
    {
        "en": {
					"FourOhFour": {
						"404Title": "error 404: girlboss not found",
						"404Subtitle": "the correct response to “pizza on the ground” is “what will it do”"
					},
					"Header": {
						// "headerTitle": "About",
						"link1label": "Discord",
						"link2label": "GitHub",
					},
					"Footer": {
						"license": "GNU General Public License v3.0",
						"link1label": "Discord",
						"link2label": "GitHub",
					},
					"Home": {
						"Title": "The PersonalGPT Project",
						"Subtitle": "The path to near-perfect digital cloning. Fully open source.",
						"card1Title": "Pycord",
						"card2Title": "OpenAI",
						"card3Title": "ElevenLabs",
						"card1Paragraph": `A modern, easy to use, feature-rich, and async ready API wrapper for Discord.`,
						"card2Paragraph": `The official OpenAI Python API library brings the bot to life.`,
						"card3Paragraph": `The official Python API provides stunningly accurate voice cloning capabilities.`,
					},
        },
    }
);