"use client"
import { Card, CardContent } from "@/components/ui/card"
import {
   Menubar,
   MenubarContent,
   MenubarItem,
   MenubarMenu,
   MenubarTrigger,
} from "@/components/ui/menubar"
import { MyAreaGraph } from "@components/charts/areagraph"
import { MyBarChart } from "@components/charts/barchart"

export default function VMCharts() {
   return (
      <Card className="p-5">
         {/* Some Charts with performance info */}
         <Menubar>
            <MenubarMenu>
               <MenubarTrigger>File</MenubarTrigger>
               <MenubarContent aria-label="Options" className="gap-0">
                  {/* Revenue chart */}
                  <MenubarItem>
                     Hello
                     <Card>
                        <CardContent>
                           {/* TODO: - the data fields need to be filled with actual data */}
                           <MyAreaGraph
                              data={[
                                 { date: "2021-12-12", value: "20" },
                                 { date: "2021-12-13", value: "30" },
                                 { date: "2021-12-14", value: "40" },
                              ]}
                              stroke="#8884d8"
                              fill="#cfeafc"
                           />
                        </CardContent>
                     </Card>
                  </MenubarItem>
                  {/* Orders chart */}
                  <MenubarItem>
                     {" "}
                     Why are you gay?
                     <Card>
                        <CardContent>
                           <MyBarChart data={[]} fill="#ffce90" />
                        </CardContent>
                     </Card>
                  </MenubarItem>
                  {/* Customers chart */}
                  <MenubarItem>
                     Dummy
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
