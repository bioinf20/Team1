def parse_LRG(filepath):
    myLRG = LRG(filepath)
    
class LRG(object):
            
    def __init__(self, filepath='LRG_292.xml'):
        import xml.etree.ElementTree as etree
        self.xmlfile = filepath
        #try:                                    # try and catch any files which are not .xml
        #    self.xmlfile=("*.xml")
        #except IOError:
        #    print "Please ensure you have entered a .xml file"

        self.tree = etree.parse(self.xmlfile)
        self.root = self.tree.getroot()
        self.id = self.set_id()                 #eg "LRG_292"
        self.sequences = self.set_sequences()   #Dictionary of seqid:sequence
        self.exons = self.set_exons()           #Nested dictionaries of exonnum,refseq,attribute
        self.set_exon_seq()

    def set_id(self):
        '''Returns LRG id string from LRG xml
            e.g. "LRG_292"          '''
        LRG_ids = self.root.findall("./fixed_annotation/id")
        for LRG in LRG_ids:
            LRG_id = LRG.text
            #assert lrg_id ==("LRG*")              # check that the ID starts with LRG to ensure we have captured the ID correctly
        return LRG_id
                

    def set_sequences(self):
        '''Returns dictionary containing sequence ids as keys, sequences as values from LRG xml
        Includes genomic, transcript, translation
        e.g. {"LRG_292":"ATCG....", LRG_292t1:"ATCG....", LRG292p1:"AACE"}'''
        sequences = {}                          #dictionary to contain all the sequences
        sequences.update(self.set_genomic_seq())    # update with the following functions to fill the dictionary
        sequences.update(self.set_cDNA())
        sequences.update(self.set_protein())
        return sequences

        
    def set_genomic_seq(self):
        '''Returns dictionary containing sequence ids as keys, sequences as values from LRG xml
        Genomic only
        e.g. {"LRG_292":"ATCG...."}'''
        genomic_id_seq = {}
        for item in (items for items in self.root[0] if items.tag == 'sequence'):   #Maybe change to self.root.find()
           genomic_seq = item.text                                                 # navigate down to the level and select the tag called sequence
        for item in self.tree.iter(tag = 'id'):                                     # extract the sequence to variable genomic seq
            genomic_id = item.text                                                  # extract the ID from Tag ID to variable genomic_ID
        return genomic_id_seq


    def set_cDNA(self):
        '''Returns dictionary containing sequence ids as keys, sequences as values from LRG xml
        Transcripts of genomic sequence only
        e.g. {"LRG_292t1":"ATCG...."}'''
        transcripts = {}
        transcript_elems = self.root.findall("./fixed_annotation/transcript")
        for transcript in transcript_elems:
            transcript_id = self.id + transcript.attrib["name"]
            for sequence in transcript.findall("./cdna/sequence"):
                transcript_seq = sequence.text
            transcripts[transcript_id] = transcript_seq
        return transcripts


    def set_protein(self):
        '''Returns dictionary containing sequence ids as keys, sequences as values from LRG xml
        Proteins from genomic transcripts only
        e.g. {"LRG_292p1":"AACE...."}'''
        proteins = {}
        protein_elems = self.root.findall("./fixed_annotation/transcript/coding_region/translation")
        for protein in protein_elems:
            print protein.tag
            protein_id = self.id + protein.attrib["name"]
            print type(protein_id)
            for sequence in protein.findall("./sequence"):
                protein_seq = sequence.text
            proteins[protein_id] = protein_seq
        return proteins


    def set_exons(self):
        '''Returns dictionary containing exon numbers as keys, dictionary as values.
           Nested dictionary contains reference sequence as keys, dictionary as values
           Second nested dictionary contains "Start","End" as keys,
               coordinates within parent reference seq as values'''
        exons = {}
        for exon in self.tree.iter(tag = 'exon'):
            if 'label' in exon.attrib:
                this_exon = {}
                print "----------------\n\nExon:" , exon.attrib["label"]
                exon_number = exon.attrib["label"]
                for coords in exon.findall('coordinates'):
                    print "\nReference: ", coords.attrib['coord_system']
                    print "Start: ", coords.attrib['start']
                    print "End: ", coords.attrib['end']
                    exon_ref = coords.attrib['coord_system']
                    exon_start = coords.attrib['start']
                    exon_end = coords.attrib['end']
                    #assert exon_start< exon_end          # assert that the exon end is after exon start
                    this_exon[exon_ref] = {"Start":exon_start,"End":exon_end}
                    print this_exon
                exons[exon_number] = this_exon
        return exons


    def get_exon_list(self):
        '''Prints a list of  sorted exon numbers and sequenes they map to within the LRG xml
           E.g. "2 ['LRG_292', 'LRG_292t1', 'LRG_292p1']"    '''

        sorted_exon_list = sorted(map(int, self.exons.keys()))
        for exon in sorted_exon_list:
            exon_refs = self.exons[str(exon)].keys()
            print "Exon:", exon, exon_refs
            
    def set_exon_seq(self, exon_list = None, upstream = 0, downstream = 0):
        '''Retrieves the exon sequence for each exon/reference sequence combination
           Saves the sequence in the second nested dictionary in self.exons
               i.e. in addition to keys "Start", "End"
                 now also contains {Sequence":exon sequence} '''
        output_fasta_file="fasta_fname.fasta" # name of the output fasta file can be changed to accept the filename as an argument
        f=open(output_fasta_file,"w") #creates an output file. If any data pre-exists it'll wipe the file
        f.close() # closes the file to prevent it being open while looping through
        if exon_list == None:
            exon_list = self.exons.keys()
            sorted_exon_list = sorted(map(int, exon_list))
            print sorted_exon_list

        for reference in self.sequences.keys():
            print "@@@@@@@@@@@@@@@@@@@@@@@@\n@@@@@@@@@@@@@@@@@@@@@@@@"
            print "\n\nRef:     ", reference, "\n"
            for exon in sorted_exon_list:
                exon = str(exon)
                print "Ref:     ", reference
                print "Exon:    ", exon
                if reference in self.exons[exon].keys():
                    exon_start = self.exons[exon][reference]["Start"]
                    exon_end = self.exons[exon][reference]["End"]
                    print "Start:   ", exon_start
                    print "End:     ", exon_end
                    print "Length:  ", int(exon_end) - int(exon_start) +1
                    adjusted_start = int(exon_start) - upstream
                    adjusted_end = int(exon_end) + downstream
                    
                    #get sequence from reference within this range
                    exon_seq = self.sequences[reference][int(exon_start)-1:int(exon_end)]
                    #save to nested dicts
                    self.exons[exon][reference]["Sequence"] = exon_seq
                        #cache results if time
                    f=open(output_fasta_file,"a") #opens the file created before
                    Fasta_str_seq=">"+reference+" Exon: "+exon+"\n"+exon_seq+"\n\n" ## assembles all the info required for the output file
                    f.write(Fasta_str_seq)
                    f.close()
                    exon_seq = self.sequences[reference][int(exon_start)-1:int(exon_end)]
                    self.exons[exon][reference]["Sequence"] = exon_seq
                    print "Sequence:", exon_seq, "\n"
                else:
                    print "Start:    -"
                    print "End:      -"
                    
   
        
    
#myLRG = LRG()

