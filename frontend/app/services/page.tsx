import ServiceStats from "@/components/servicestats"

import Navbar from "@components/navbar"
import Sidebar from "@components/sidebar"

export default function Home() {
   return (
      <main>
         <Navbar />
         <div className="flex">
            <Sidebar />
            <div className="container">
               <ServiceStats />
            </div>
         </div>
      </main>
   )
}
