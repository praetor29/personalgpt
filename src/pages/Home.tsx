import { memo } from "react";
import { GlHero } from "gitlanding/GlHero/GlHero";
import { GlCards } from "gitlanding/GlCards";
import { GlLogoCard } from "gitlanding/GlCards/GlLogoCard";
import { GlCheckList } from "gitlanding/GlCheckList";
import { GlSectionDivider } from "gitlanding/GlSectionDivider";
import { declareComponentKeys, useTranslation } from "i18n";

// Import the useIsDarkModeEnabled hook from onyxia-ui (custom!!)
import { useIsDarkModeEnabled } from 'onyxia-ui/lib/useIsDarkModeEnabled';

// main image
import pfp from "assets/img/taylor/pfp.png";

// pycord logo
import pycord from "assets/icons/pycord.png";

// openai logo
import darkOpenai from "assets/icons/openai/dark.svg";
import lightOpenai from "assets/icons/openai/light.svg";

// elevenlabs logo
import lightElevenlabs from "assets/icons/elevenlabs/light.png";
import darkElevenlabs from "assets/icons/elevenlabs/dark.png";

export const Home = memo(() => {
	const { t } = useTranslation({ Home });
	const { isDarkModeEnabled } = useIsDarkModeEnabled(); // custom!!

	// light vs dark saga (custom!!)
	const openai = isDarkModeEnabled ? darkOpenai : lightOpenai;
	const elevenlabs = isDarkModeEnabled ? darkElevenlabs : lightElevenlabs;
	

	return (
		<>
			<GlHero
				title={t("Title")}
				subTitle={t("Subtitle")}
				illustration={{
					"type": "image",
					"src": pfp,
					"hasShadow": false
				}}
				hasLinkToSectionBellow={true}
			/>
			
			<GlCheckList
          hasAnimation={true}
          heading="Core Features"
          elements={[
            {
              "title": "Finetuning Support",
              "description": "Utilizes cutting-edge `gpt-3.5-turbo-1106` fine-tuned models for precise user mimicry, offering unparalleled personalization and accuracy in responses."
            },
            {
              "title": "GPT-4 Vision",
              "description": "Employs the new `gpt-4-vision-preview` model for advanced **image recognition**, showcasing state-of-the-art capabilities in visual data interpretation and analysis."
            },
            {
              "title": "Configurable Memory",
              "description": "Features a highly robust and adaptable `asyncio` queue, employing a dependable **First In, First Out** (FIFO) strategy to guarantee reliable and lossless data handling."
            },
            {
              "title": "Fully Asynchronous Processing",
              "description": "Designed to manage high volumes of concurrent messages efficiently, ensuring seamless performance without any overload."
            },
            {
              "title": "Customizable Parameters",
              "description": "Offers extensive customization options for the bot's front-end. Easily modify all aspects via the [Discord Developer Portal](https://discord.com/developers/applications) complemented by a user-friendly configuration file, ensuring a tailored experience."
            },
            {
              "title": "Discord Voice Chat (In Dev)",
              "description": "Integrates OpenAI's `whisper-1` STT model alongside ElevenLab's TTS voice cloning technology, paving the way for a simulated audio conversation experience on Discord. Anticipate a groundbreaking conversational experience."
            }
          ]}
		/>
			
			<GlSectionDivider />

			<GlCards
				title="Uses open source libraries"
			>
				<GlLogoCard
					title={t("card1Title")}
					paragraph={t("card1Paragraph")}
					iconUrls={[pycord]}

					buttonLabel="View project"
					link={{
						href: "https://github.com/Pycord-Development/pycord"
					}}
				/>
				<GlLogoCard
					title={t("card2Title")}
					paragraph={t("card2Paragraph")}
					iconUrls={[openai]}

					buttonLabel="View project"
					link={{
						href: "https://github.com/openai/openai-python"
					}}
				/>

				<GlLogoCard
					title={t("card3Title")}
					paragraph={t("card3Paragraph")}
					iconUrls={[elevenlabs]}

					buttonLabel="View project"
					link={{
						href: "https://github.com/elevenlabs/elevenlabs-python"
					}}
				/>
			</GlCards>
		</>
	);
});

export const { i18n } = declareComponentKeys<
	| "Title"
	| "Subtitle"
	| "card1Title"
	| "card2Title"
	| "card3Title"
	| "card1Paragraph"
	| "card2Paragraph"
	| "card3Paragraph"
>()({ Home });