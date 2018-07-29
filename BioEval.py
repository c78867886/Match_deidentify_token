###
 # <p>Title:  </p>
 # <p>Create Date: 21:23:36 01/28/18</p>
 # <p>Copyright: College of Medicine </p>
 # <p>Organization: University of Florida</p>
 # @author Yonghui Wu
 # @version 1.0
 # <p>Description: </p>
 ##

class PRF:
    def __init__(self):
        self.true=0
        self.false=0
        

class BioEval:
    def __init__(self,ifn):
        self.ifn=ifn
        self.acc=PRF()
        self.all_strict=PRF()
        self.all_relax=PRF()
        self.cate_strict={}
        self.cate_relax={}

        self.gold_all=0
        self.gold_cate={}
        #self.entities=[]
        
    def eval_fn(self):
        text=file(self.ifn).read().strip().lower()
        secs=text.split('\n\n')
        for sec in secs:
            sec=sec.strip()
            lines=sec.split('\n')
            bio=[]
            for line in lines:
                words=line.split(None)
                #words.append(words[-1])
                bio.append(words)

            self.handle(bio)
        self.prf()

    def feed_bio(self,bio):
        self.handle(bio)

    def train_msg(self):
        stt="Entities: "
        for k,v in self.gold_cate.iteritems():
            stt=stt+k+":"+str(v)+"  "
        if (self.acc.true+self.acc.false)> 0:
            acc=float(self.acc.true)/(self.acc.true+self.acc.false)
        else:
            acc=0.0
        if (self.all_strict.true+self.all_strict.false) > 0 and self.gold_all>0:
            pre = float(self.all_strict.true)/(self.all_strict.true+self.all_strict.false)
            rec = float(self.all_strict.true)/self.gold_all
            if pre+rec>0.0:
                f1=2*pre*rec/(pre+rec)
            else:
                f1=0.0
        else:
            pre=0.0
            rec=0.0
            f1=0.0

        #all_relex
        if (self.all_relax.true+self.all_relax.false) > 0 and self.gold_all>0:
            rpre = float(self.all_relax.true)/(self.all_relax.true+self.all_relax.false)
            rrec = float(self.all_relax.true)/self.gold_all
            if (rpre+rrec) > 0.0:
                rf1=2*rpre*rrec/(rpre+rrec)
            else:
                rf1=0.0
        else:
            rpre=0.0
            rrec=0.0
            rf1=0.0

        return([stt,f1,pre,rec,rf1,rpre,rrec,acc])

    def prf(self):
        # calcualte scores
        # all_strict
        

        print "Total %s entities " % self.gold_all
        for k,v in self.gold_cate.iteritems():
            print "    %s : %s" % (k,v)

        acc=float(self.acc.true)/(self.acc.true+self.acc.false)
        print "\nAccuracy : %s" % acc

        pre = float(self.all_strict.true)/(self.all_strict.true+self.all_strict.false)
        rec = float(self.all_strict.true)/self.gold_all
        f1=2*pre*rec/(pre+rec)

        print "\n\nStrict score ----- "
        print 'precision : %s , recall : %s , f1 : %s' % (pre,rec,f1)
        print 'find : %s , true : %s , false : %s' % (self.all_strict.true+self.all_strict.false,self.all_strict.true,self.all_strict.false)

        #all_relex
        pre = float(self.all_relax.true)/(self.all_relax.true+self.all_relax.false)
        rec = float(self.all_relax.true)/self.gold_all
        f1=2*pre*rec/(pre+rec)

        print "\nRelax score -----"
        print 'precision : %s , recall : %s , f1 : %s' % (pre,rec,f1)
        print 'find : %s , true : %s , false : %s' % (self.all_relax.true+self.all_relax.false,self.all_relax.true,self.all_relax.false)

        ##category score
        print "\nstrict score by cate -----"
        for k,v in self.cate_strict.iteritems():
            pre = float(v.true)/(v.true+v.false)
            rec = float(v.true)/self.gold_cate[k]
            f1=2*pre*rec/(pre+rec)

            print "Cate : %s, precision : %s , recall : %s , f1 : %s" % (k,pre,rec,f1)
            print 'find : %s , true : %s , false : %s' % (v.true+v.false,v.true,v.false)

        print "\nrelax score by cate -----"
        for k,v in self.cate_relax.iteritems():
            pre = float(v.true)/(v.true+v.false)
            rec = float(v.true)/self.gold_cate[k]
            f1=2*pre*rec/(pre+rec)

            print "Cate : %s, precision : %s , recall : %s , f1 : %s" % (k,pre,rec,f1)
            print 'find : %s , true : %s , false : %s' % (v.true+v.false,v.true,v.false)
        

    def same(self,bio,starti,endi):
        '''
        whether the ner (starti : endi) is exactly match
        '''
        flag=True
        pcate=bio[starti][-1][2:]
        if bio[starti][-2].startswith("i-"):
            cate=bio[starti][-2][2:]
            if cate != pcate:
                flag=False
            else:
                #check starti-1
                if starti -1 >= 0 and bio[starti-1][-2] == "i-"+cate or bio[starti-1][-2] == "b-"+cate:
                    flag=False
            if flag:
                for i in range(starti+1,endi):
                    if bio[i][-2] != "i-"+cate:
                        flag=False
            if flag:# check endi
                if endi < len(bio) and bio[endi][-2] == "i-"+cate:
                    flag=False
        elif bio[starti][-2].startswith("b-"):
            cate=bio[starti][-2][2:]
            if cate != pcate:
                flag=False
            # do not need check starti -1
            if flag:
                for i in range(starti+1,endi):
                    if bio[i][-2] != "i-"+cate:
                        flag=False
            if flag:# check endi
                if endi < len(bio) and bio[endi][-2] == "i-"+cate:
                    flag=False
        else:
            flag=False
            
        return flag

    def overlap(self,bio,starti,endi):
        flag=False
        for i in range(starti,endi):
            if len(bio[i][-2])> 2 and bio[i][-1][2:] == bio[i][-2][2:]:
                flag=True
                break
        return flag
        

    def add_tp_strict(self,cate):
        self.all_strict.true=self.all_strict.true+1
        self.all_relax.true=self.all_relax.true+1
        if cate not in self.cate_strict:
            self.cate_strict[cate]=PRF()
        self.cate_strict[cate].true=self.cate_strict[cate].true+1
        if cate not in self.cate_relax:
            self.cate_relax[cate]=PRF()
        self.cate_relax[cate].true=self.cate_relax[cate].true+1

    def add_tp_overlap(self,cate):
        self.all_relax.true=self.all_relax.true+1
        if cate not in self.cate_relax:
            self.cate_relax[cate]=PRF()
        self.cate_relax[cate].true=self.cate_relax[cate].true+1
        # treat as false by strict
        self.all_strict.false=self.all_strict.false+1
        if cate not in self.cate_strict:
            self.cate_strict[cate]=PRF()
        self.cate_strict[cate].false=self.cate_strict[cate].false+1
        

    def add_nolap(self,cate):
        self.all_strict.false=self.all_strict.false+1
        self.all_relax.false=self.all_relax.false+1

        if cate not in self.cate_strict:
            self.cate_strict[cate]=PRF()
        self.cate_strict[cate].false=self.cate_strict[cate].false+1

        if cate not in self.cate_relax:
            self.cate_relax[cate]=PRF()
        self.cate_relax[cate].false=self.cate_relax[cate].false+1

    
                    
    def handle(self,bio):
        #print bio
        obio = bio
        bio = []

        for each in obio:
            if len(each) > 1:
                bio.append(each)

        llen=len(bio)

        #accumulate accuracy data
        for i in range(llen):
            try:
                if bio[i][-1].strip() == bio[i][-2].strip():
                    self.acc.true=self.acc.true+1
                else:
                    self.acc.false=self.acc.false+1
            except:
                print bio[i]

        i=0
        # handle system prediction
        while i < llen:
            if bio[i][-1] == 'o':
                i=i+1
            else:
                # find the start and end pos
                starti=i
                endi=i+1
                cate=bio[starti][-1][2:].strip()
                while endi<llen and bio[endi][-1].startswith('i-'+cate):
                    endi=endi+1
                #find the categor
                # exactly match
                if self.same(bio,starti,endi):
                    self.add_tp_strict(cate)
                # overlap        
                elif self.overlap(bio,starti,endi):
                    self.add_tp_overlap(cate)
                else: # no overlap
                    self.add_nolap(cate)

                i=endi

        #handle the ground truth label
        i=0
        while i< llen:
            if bio[i][-2] == 'o':
                i=i+1
            else:
                # find the start and end pos
                starti=i
                endi=i+1
                cate=bio[starti][-2][2:].strip()
                while endi<llen and bio[endi][-2].startswith('i-'+cate):
                    endi=endi+1
                self.gold_all=self.gold_all+1
                if cate not in self.gold_cate:
                    self.gold_cate[cate]=0
                self.gold_cate[cate]=self.gold_cate[cate]+1

                i=endi
        
        

if __name__ == "__main__":
    import sys
    ifn = "for_conell_eval.txt"
    eva= BioEval(ifn)
    eva.eval_fn()
    eva.train_msg()
    


        

    
