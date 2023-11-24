import { memo } from "react";
import { declareComponentKeys } from "i18nifty";
import { useTranslation } from "i18n";

import { GlHero } from "gitlanding/GlHero/GlHero";
import pfp from "assets/img/taylor/pfp.png";

export const FourOhFour = memo(() => {
    const { t } = useTranslation({ FourOhFour });

    return (
        <GlHero
			title={t("404Title")}
            subTitle={t("404Subtitle")}
			illustration={{
                "type": "image",
                "src": pfp,
                "hasShadow": true
            }}
			hasAnimation={true}
		/>
    );
});

export const { i18n } = declareComponentKeys<
| "404Title"
| "404Subtitle"
>()({
    FourOhFour,
});