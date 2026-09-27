self.addEventListener('notificationclick',event=>{
  event.notification.close();
  event.waitUntil((async()=>{
    const pages=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    for(const page of pages)page.postMessage({type:'stop-mir4-alarm'});
    if(event.action!=='stop'&&pages[0])await pages[0].focus();
  })());
});
