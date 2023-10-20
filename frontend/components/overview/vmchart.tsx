"use client"
import { Card, CardContent } from "@/components/ui/card"
import { MyAreaGraph } from "@/components/ui/charts/areagraph"
import { MyLineChart } from "@/components/ui/charts/linechart"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function VMChart({ data }: any) {
   return (
      <div className="container mx-auto mt-12 mb-8">
         <Card className="p-5">
            <Tabs defaultValue="revenue">
               <TabsList>
                  <TabsTrigger value="cpu">CPU Usage</TabsTrigger>
                  <TabsTrigger value="ram">RAM Usage</TabsTrigger>
                  <TabsTrigger value="network">Network Usage</TabsTrigger>
               </TabsList>
               {/* CPU Usage */}
               <TabsContent value="cpu">
                  <Card>
                     <CardContent className="p-6">
                        <MyAreaGraph
                           name="CPU Usage %"
                           data={data.cpuData}
                           stroke="#8884d8"
                           fill="#cfeafc"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
               {/* RAM Usage */}
               <TabsContent value="ram">
                  <Card>
                     <CardContent className="p-6">
                        <MyAreaGraph
                           name="RAM Usage %"
                           data={data.ramData}
                           stroke="#00bd56"
                           fill="#ccf3f3"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
               {/* Network Usage */}
               <TabsContent value="network">
                  <Card>
                     <CardContent className="p-6">
                        <MyLineChart
                           data={data.netData}
                           stroke1="#8884d8"
                           stroke2="#82ca9d"
                           name1="Received in kB/s"
                           name2="Transmitted in kB/s"
                        />
                     </CardContent>
                  </Card>
               </TabsContent>
            </Tabs>
         </Card>
      </div>
   )
}
