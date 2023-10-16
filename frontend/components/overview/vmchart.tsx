"use client"
import { Card, CardContent } from "@/components/ui/card"
import { MyAreaGraph } from "@/components/ui/charts/areagraph"
import { MyBarChart } from "@/components/ui/charts/barchart"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function VMChart({ data }: any) {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <Card className="p-5">
            <Tabs defaultValue="revenue">
               <TabsList>
                  <TabsTrigger value="revenue">CPU Usage</TabsTrigger>
                  <TabsTrigger value="orders">RAM Usage</TabsTrigger>
                  <TabsTrigger value="customers">Network Usage</TabsTrigger>
               </TabsList>
               {/* CPU Usage */}
               <TabsContent value="revenue">
                  <Card>
                     <CardContent className="p-6">
                        <MyAreaGraph
                           data={data.cpuData}
                           stroke="#8884d8"
                           fill="#cfeafc"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
               {/* RAM Usage */}
               <TabsContent value="orders">
                  <Card>
                     <CardContent className="p-6">
                        <MyBarChart data={data.ramData} fill="#ffce90" />
                     </CardContent>
                  </Card>
               </TabsContent>
               {/* Network Usage */}
               <TabsContent value="customers">
                  <Card>
                     <CardContent className="p-6">
                        <MyAreaGraph
                           data={data.netData}
                           stroke="#00bd56"
                           fill="#ccf3f3"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
            </Tabs>
         </Card>
      </div>
   )
}
