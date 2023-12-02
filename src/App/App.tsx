import { GlTemplate } from "gitlanding/GlTemplate";
import { Header } from "./Header";
import { Footer } from "./Footer";
import { useEffect } from 'react';
import { useRoute, routes } from "../router";
import { Home } from "../pages/Home";
// import { PageExample } from "../pages/PageExample"; // removed example page
import { FourOhFour } from "../pages/FourOFour";
import { ThemeProvider } from "../theme";

export function App() {
	const route = useRoute();

	useEffect(() => {
        const queryParams = new URLSearchParams(window.location.search);
        if (queryParams.get('notFound')) {
            // Navigate to the 404 route
            routes.FourOhFour().push();
        }
    }, []);

	return (
		<ThemeProvider>
			<GlTemplate
				header={<Header />}
				headerOptions={{
					"position": "sticky",
					"isRetracted": "smart",
				}}
				footer={<Footer />}
				body={
					(()=>{
						switch(route.name){
							case "home": return <Home />;
							case "FourOhFour": return <FourOhFour />;
							default : return <FourOhFour />;
						}
					})()
				}
			/>
		</ThemeProvider>
	);
}