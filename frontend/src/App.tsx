import { ErrorComponent, Refine } from "@refinedev/core"
import { RefineKbar, RefineKbarProvider } from "@refinedev/kbar"
import routerBindings, {
   DocumentTitleHandler,
   NavigateToResource,
   UnsavedChangesNotifier,
} from "@refinedev/react-router-v6"
import dataProvider from "@refinedev/simple-rest"

//////////  react stuff  //////////
import { useTranslation } from "react-i18next"
import { BrowserRouter, Outlet, Route, Routes } from "react-router-dom"

//////////  components  //////////
import { Layout } from "./components/layout"

//////////  pages  //////////
import {
   CategoryCreate,
   CategoryEdit,
   CategoryList,
   CategoryShow,
} from "./pages/categories"
import { DashboardPage } from "./pages/dashboard/DashboardPage"

function App() {
   const { t, i18n } = useTranslation()

   const i18nProvider = {
      translate: (key: string, params: object) => t(key, params),
      changeLocale: (lang: string) => i18n.changeLanguage(lang),
      getLocale: () => i18n.language,
   }
   return (
      <BrowserRouter>
         <RefineKbarProvider>
            <Refine
               dataProvider={dataProvider("https://api.finefoods.refine.dev")}
               i18nProvider={i18nProvider}
               routerProvider={routerBindings}
               resources={[
                  {
                     name: "categories",
                     list: "/categories",
                     create: "/categories/create",
                     edit: "/categories/edit/:id",
                     show: "/categories/show/:id",
                     meta: {
                        canDelete: true,
                     },
                  },
                  {
                     name: "dashboard",
                     list: "/dashboard",
                  },
               ]}
               options={{
                  syncWithLocation: true,
                  warnWhenUnsavedChanges: true,
                  projectId: "rhafgh-aLP9JS-0GTfcM",
               }}
            >
               <Routes>
                  <Route
                     element={
                        <Layout>
                           <Outlet />
                        </Layout>
                     }
                  >
                     <Route
                        index
                        element={<NavigateToResource resource="dashboard" />}
                     />
                     <Route path="/dashboard">
                        <Route index element={<DashboardPage />} />
                     </Route>
                     <Route path="/categories">
                        <Route index element={<CategoryList />} />
                        <Route path="create" element={<CategoryCreate />} />
                        <Route path="edit/:id" element={<CategoryEdit />} />
                        <Route path="show/:id" element={<CategoryShow />} />
                     </Route>
                     <Route path="*" element={<ErrorComponent />} />
                  </Route>
               </Routes>

               <RefineKbar />
               <UnsavedChangesNotifier />
               <DocumentTitleHandler />
            </Refine>
         </RefineKbarProvider>
      </BrowserRouter>
   )
}

export default App
