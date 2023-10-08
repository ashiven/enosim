"use client"
import { Card, CardContent } from "@/components/ui/card"
import {
   Menubar,
   MenubarContent,
   MenubarItem,
   MenubarMenu,
} from "@/components/ui/menubar"
import { MyAreaGraph } from "@components/charts/areagraph"
import { MyBarChart } from "@components/charts/barchart"

export default function VMCharts() {
   return (
      <Card className="p-5">
         {/* Some Charts with performance info */}
         <Menubar>
            <MenubarMenu>
               <MenubarContent aria-label="Options" className="gap-0">
                  {/* Revenue chart */}
                  <MenubarItem key="revenue" title="Revenue">
                     <Card>
                        <CardContent>
                           {/* TODO: - the data fields need to be filled with actual data */}
                           <MyAreaGraph
                              data={[]}
                              stroke="#8884d8"
                              fill="#cfeafc"
                           />
                        </CardContent>
                     </Card>
                  </MenubarItem>
                  {/* Orders chart */}
                  <MenubarItem key="orders" title="Orders">
                     <Card>
                        <CardContent>
                           <MyBarChart data={[]} fill="#ffce90" />
                        </CardContent>
                     </Card>
                  </MenubarItem>
                  {/* Customers chart */}
                  <MenubarItem key="customers" title="Customers">
                     <Card>
                        <CardContent>
                           <MyAreaGraph
                              data={[]}
                              stroke="#00bd56"
                              fill="#ccf3f3"
                           />
                        </CardContent>
                     </Card>
                  </MenubarItem>
               </MenubarContent>
            </MenubarMenu>
         </Menubar>
      </Card>
   )
}
