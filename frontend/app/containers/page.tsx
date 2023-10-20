import ContainerCharts from "@/components/overview/vmcharts"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main>
         <Navbar />
         <div className="flex">
            <Sidebar />
            <div className="container">
               <ContainerCharts />
            </div>
         </div>
      </main>
   )
}
